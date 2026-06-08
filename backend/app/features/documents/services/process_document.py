import asyncio
from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.modules.rag.json_schema import ExtractedEntities
from app.shared.enums import DocumentStatus

from ..schemas.responses import ProcessDocumentResponse
from .helpers.document_processing_job import run_document_processing_job


class ProcessDocumentService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, document_id: UUID) -> ProcessDocumentResponse:
        # check document exists
        doc = await self._uow.document_repo.get_by_id(document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")

        # check scenario exists
        scenario = await self._uow.scenario_repo.get_by_id(doc.scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # check document status
        if doc.status == DocumentStatus.PROCESSING:
            raise HTTPException(status_code=409, detail="Document is processing")
        if doc.status == DocumentStatus.COMPLETED:
            raise HTTPException(status_code=409, detail="Document already processed")
        if doc.status not in (DocumentStatus.READY, DocumentStatus.FAILED):
            raise HTTPException(status_code=400, detail="Invalid document status")

        # check document markdown path
        if not doc.md_path:
            raise HTTPException(status_code=400, detail="Document markdown not found")

        # update document status to processing
        doc.status = DocumentStatus.PROCESSING
        await self._uow.session.flush()

        asyncio.create_task(
            run_document_processing_job(
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

        return ProcessDocumentResponse(
            document_id=document_id,
            status=DocumentStatus.PROCESSING,
            message="Document processing started",
            entities=result.entities,
            relationships=result.relationships,
        )
