from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.documents.schemas.processing_pipeline import (
    ChunkStepResponse,
    ClearGraphStepResponse,
    DocumentProcessingPipelineResponse,
    EntityEmbeddingStepResponse,
    EntityExtractionStepResponse,
    GraphBuildStepResponse,
    PrepareStepResponse,
    ProcessingStepResponse,
)
from app.repositories.document_processing_run_repo import (
    DocumentProcessingRunRepository,
)
from app.shared.enums import ProcessingStepId

_STEP_RESPONSE_BY_ID: dict[ProcessingStepId, type] = {
    ProcessingStepId.PREPARE: PrepareStepResponse,
    ProcessingStepId.CLEAR_GRAPH: ClearGraphStepResponse,
    ProcessingStepId.CHUNK: ChunkStepResponse,
    ProcessingStepId.ENTITY_EXTRACTION: EntityExtractionStepResponse,
    ProcessingStepId.GRAPH_BUILD: GraphBuildStepResponse,
    ProcessingStepId.ENTITY_EMBEDDING: EntityEmbeddingStepResponse,
}


class GetDocumentProcessingPipelineService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, document_id: UUID) -> DocumentProcessingPipelineResponse:
        doc = await self._uow.document_repo.get_by_id(document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")

        run_repo = DocumentProcessingRunRepository(self._uow.session)
        run = await run_repo.get_by_document_id(document_id)
        if run is None:
            raise HTTPException(
                status_code=404, detail="Document processing pipeline not found"
            )

        steps: list[ProcessingStepResponse] = []
        for step_data in run.steps:
            step_id = ProcessingStepId(step_data["id"])
            response_cls = _STEP_RESPONSE_BY_ID[step_id]
            steps.append(response_cls.model_validate(step_data))

        return DocumentProcessingPipelineResponse(
            document_id=document_id,
            filename=doc.filename,
            started_at=run.started_at,
            completed_at=run.completed_at,
            total_duration_ms=run.total_duration_ms,
            steps=steps,
        )
