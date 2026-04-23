from pathlib import Path
from uuid import UUID

from fastapi import HTTPException

from app.core.setting import get_settings
from app.db.uow import UnitOfWorkDependency
from ..schemas.responses import DocumentMarkdownResponse


class GetDocumentMarkdownService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, document_id: UUID) -> DocumentMarkdownResponse:
        doc = await self._uow.document_repo.get_by_id(document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")
        if not doc.md_path:
            raise HTTPException(status_code=404, detail="Markdown not available")

        settings = get_settings()
        path = Path(settings.UPLOAD_DIR) / doc.md_path
        if not path.exists():
            raise HTTPException(status_code=404, detail="Markdown file not found")

        return DocumentMarkdownResponse(content=path.read_text(encoding="utf-8"))
