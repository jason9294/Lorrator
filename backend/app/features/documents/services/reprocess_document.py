import asyncio
from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.modules.rag.json_schema import ExtractedEntities
from app.shared.enums import DocumentStatus

from ..schemas.responses import ProcessDocumentResponse
from .helpers.document_processing_job import run_document_processing_job


class ReprocessDocumentService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, document_id: UUID) -> ProcessDocumentResponse:
        doc = await self._uow.document_repo.get_by_id(document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")

        scenario = await self._uow.scenario_repo.get_by_id(doc.scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")

        if doc.status == DocumentStatus.PROCESSING:
            raise HTTPException(status_code=409, detail="Document is processing")
        if doc.status not in (DocumentStatus.COMPLETED, DocumentStatus.FAILED):
            raise HTTPException(
                status_code=400,
                detail="Only completed or failed documents can be reprocessed",
            )

        if not doc.md_path:
            raise HTTPException(status_code=400, detail="Document markdown not found")

        documents = await self._uow.document_repo.list_by_scenario(doc.scenario_id)
        legacy_untagged_chunks = len(documents) == 1

        doc.status = DocumentStatus.PROCESSING
        await self._uow.session.flush()

        asyncio.create_task(
            run_document_processing_job(
                document_id=document_id,
                scenario_id=doc.scenario_id,
                graph_group_id=str(scenario.graph_group_id),
                notify_user_id=scenario.creator_id,
                clear_existing=True,
                legacy_untagged_chunks=legacy_untagged_chunks,
            )
        )

        result = ExtractedEntities(
            entities=[],
            relationships=[],
        )

        return ProcessDocumentResponse(
            document_id=document_id,
            status=DocumentStatus.PROCESSING,
            message="Document reprocessing started",
            entities=result.entities,
            relationships=result.relationships,
        )
