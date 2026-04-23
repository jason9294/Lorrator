import asyncio
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_settings
from app.core.websocket.manager import get_ws_connection_manager
from app.db.sql import async_engine
from app.db.uow import UnitOfWorkDependency
from app.modules.rag.chunker import chunk_text
from app.modules.rag.json_schema import ExtractedEntities
from app.uncategorized.entity_types import NPC, Ending, Event, Item, Location
from app.shared.enums import DocumentStatus
from graphiti_core import Graphiti
from graphiti_core.utils.datetime_utils import utc_now

from ..schemas.responses import ProcessDocumentResponse

settings = get_settings()


class ProcessDocumentService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, document_id: UUID) -> ProcessDocumentResponse:
        doc = await self._uow.document_repo.get_by_id(document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")

        scenario = await self._uow.scenario_repo.get_by_id(doc.scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # only allow processing once (retry only when FAILED)
        if doc.status == DocumentStatus.PROCESSING:
            raise HTTPException(status_code=409, detail="Document is processing")
        if doc.status == DocumentStatus.COMPLETED:
            raise HTTPException(status_code=409, detail="Document already processed")
        if doc.status not in (DocumentStatus.READY, DocumentStatus.FAILED):
            raise HTTPException(status_code=400, detail="Invalid document status")

        if not doc.md_path:
            raise HTTPException(status_code=400, detail="Document markdown not found")

        doc.status = DocumentStatus.PROCESSING
        await self._uow.session.flush()

        # run async processing in background (detached from request session)
        asyncio.create_task(
            _process_document_job(
                document_id=document_id,
                scenario_id=doc.scenario_id,
                graph_group_id=str(scenario.graph_group_id),
                notify_user_id=scenario.creator_id,
            )
        )

        result = ExtractedEntities(
            entities=[],
            relationships=[],
        )

        # for task in tasks:
        #     result.entities.extend(task.entities)
        #     result.relationships.extend(task.relationships)

        return ProcessDocumentResponse(
            document_id=document_id,
            status=DocumentStatus.PROCESSING,
            message="Document processing started",
            entities=result.entities,
            relationships=result.relationships,
        )


async def _process_document_job(
    *,
    document_id: UUID,
    scenario_id: UUID,
    graph_group_id: str,
    notify_user_id: UUID,
) -> None:
    manager = get_ws_connection_manager()
    await manager.send_to_user(
        notify_user_id,
        message_type="documents.process_updated",
        payload={
            "document_id": str(document_id),
            "scenario_id": str(scenario_id),
            "status": DocumentStatus.PROCESSING.value,
        },
    )

    async with AsyncSession(async_engine) as session:
        try:
            # load document
            from sqlmodel import select

            from app.models import DocumentModel

            stmt = select(DocumentModel).where(DocumentModel.id == document_id)
            res = await session.execute(stmt)
            doc = res.scalar_one_or_none()
            if doc is None:
                return

            upload_root = Path(settings.UPLOAD_DIR)
            path = upload_root / (doc.md_path or "")
            if not path.exists():
                doc.status = DocumentStatus.FAILED
                await session.commit()
                await manager.send_to_user(
                    notify_user_id,
                    message_type="documents.process_updated",
                    payload={
                        "document_id": str(document_id),
                        "scenario_id": str(scenario_id),
                        "status": DocumentStatus.FAILED.value,
                        "error": "Markdown file missing",
                    },
                )
                return

            content = path.read_text(encoding="utf-8")
            chunks = chunk_text(content)

            graphiti = Graphiti(
                settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD
            )
            try:
                await graphiti.build_indices_and_constraints()
                for i, chunk in enumerate(chunks):
                    await graphiti.add_episode(
                        name=f"TRPG Scenario {i}",
                        episode_body=chunk.text,
                        source_description="TRPG Scenario Chunk",
                        reference_time=utc_now(),
                        group_id=graph_group_id,
                        entity_types={
                            "NPC": NPC,
                            "Event": Event,
                            "Location": Location,
                            "Item": Item,
                            "Ending": Ending,
                        },
                    )
            finally:
                await graphiti.close()

            doc.status = DocumentStatus.COMPLETED
            await session.commit()
            await manager.send_to_user(
                notify_user_id,
                message_type="documents.process_updated",
                payload={
                    "document_id": str(document_id),
                    "scenario_id": str(scenario_id),
                    "status": DocumentStatus.COMPLETED.value,
                },
            )
        except Exception as e:
            try:
                from sqlmodel import select

                from app.models import DocumentModel

                stmt = select(DocumentModel).where(DocumentModel.id == document_id)
                res = await session.execute(stmt)
                doc = res.scalar_one_or_none()
                if doc is not None:
                    doc.status = DocumentStatus.FAILED
                    await session.commit()
            except Exception:
                ...
            await manager.send_to_user(
                notify_user_id,
                message_type="documents.process_updated",
                payload={
                    "document_id": str(document_id),
                    "scenario_id": str(scenario_id),
                    "status": DocumentStatus.FAILED.value,
                    "error": str(e),
                },
            )
