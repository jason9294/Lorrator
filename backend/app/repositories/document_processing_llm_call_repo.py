from uuid import UUID

from sqlalchemy import delete
from sqlmodel import col, select

from app.models import DocumentProcessingLlmCallModel

from ._base_repo import BaseRepository


class DocumentProcessingLlmCallRepository(BaseRepository):
    async def create_many(
        self, calls: list[DocumentProcessingLlmCallModel]
    ) -> list[DocumentProcessingLlmCallModel]:
        for call in calls:
            self.session.add(call)
        await self.session.flush()
        return calls

    async def delete_by_run_id(self, run_id: UUID) -> None:
        await self.session.execute(
            delete(DocumentProcessingLlmCallModel).where(
                col(DocumentProcessingLlmCallModel.run_id) == run_id
            )
        )
        await self.session.flush()

    async def list_by_run_id(
        self, run_id: UUID
    ) -> list[DocumentProcessingLlmCallModel]:
        statement = (
            select(DocumentProcessingLlmCallModel)
            .where(col(DocumentProcessingLlmCallModel.run_id) == run_id)
            .order_by(col(DocumentProcessingLlmCallModel.sequence))
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())


def provide_document_processing_llm_call_repo_cls() -> (
    type[DocumentProcessingLlmCallRepository]
):
    return DocumentProcessingLlmCallRepository
