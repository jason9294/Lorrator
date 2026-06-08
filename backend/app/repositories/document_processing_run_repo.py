from uuid import UUID

from sqlmodel import select

from app.models import DocumentProcessingRunModel

from ._base_repo import BaseRepository


class DocumentProcessingRunRepository(BaseRepository):
    async def get_by_document_id(
        self, document_id: UUID
    ) -> DocumentProcessingRunModel | None:
        statement = select(DocumentProcessingRunModel).where(
            DocumentProcessingRunModel.document_id == document_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def upsert(self, run: DocumentProcessingRunModel) -> DocumentProcessingRunModel:
        existing = await self.get_by_document_id(run.document_id)
        if existing is not None:
            existing.pipeline_id = run.pipeline_id
            existing.status = run.status
            existing.started_at = run.started_at
            existing.completed_at = run.completed_at
            existing.total_duration_ms = run.total_duration_ms
            existing.steps = run.steps
            existing.error = run.error
            await self.session.flush()
            return existing

        self.session.add(run)
        await self.session.flush()
        return run


def provide_document_processing_run_repo_cls() -> type[DocumentProcessingRunRepository]:
    return DocumentProcessingRunRepository
