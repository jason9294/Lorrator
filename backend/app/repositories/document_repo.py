from uuid import UUID

from sqlmodel import select

from app.models import DocumentModel

from ._base_repo import BaseRepository


class DocumentRepository(BaseRepository):
    async def get_by_id(self, document_id: UUID) -> DocumentModel | None:
        statement = select(DocumentModel).where(DocumentModel.id == document_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_scenario(self, scenario_id: UUID) -> list[DocumentModel]:
        statement = select(DocumentModel).where(DocumentModel.scenario_id == scenario_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(
        self,
        scenario_id: UUID,
        filename: str,
        content_type: str | None,
        file_path: str,
        md_path: str | None,
    ) -> DocumentModel:
        doc = DocumentModel(
            scenario_id=scenario_id,
            filename=filename,
            content_type=content_type,
            file_path=file_path,
            md_path=md_path,
        )
        self.session.add(doc)
        await self.session.flush()
        return doc


def provide_document_repo_cls() -> type[DocumentRepository]:
    return DocumentRepository
