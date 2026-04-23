from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException

from app.core.setting import get_settings
from app.db.uow import UnitOfWorkDependency


@dataclass(frozen=True, slots=True)
class OriginalDocumentFile:
    path: Path
    media_type: str
    filename: str


class DownloadOriginalDocumentService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, document_id: UUID) -> OriginalDocumentFile:
        doc = await self._uow.document_repo.get_by_id(document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")

        settings = get_settings()
        path = Path(settings.UPLOAD_DIR) / doc.file_path
        if not path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return OriginalDocumentFile(
            path=path,
            media_type=doc.content_type or "application/octet-stream",
            filename=doc.filename,
        )
