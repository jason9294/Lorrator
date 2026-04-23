from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from markitdown import MarkItDown

from app.core.setting import get_settings
from app.db.uow import UnitOfWorkDependency
from app.features.scenarios.schemas.responses import DocumentResponse
from app.shared.utils import uuid7
from app.shared.utils.common_utils import safe_upload_filename

settings = get_settings()


class UploadScenarioDocumentService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(
        self,
        scenario_id: UUID,
        *,
        file_content: bytes,
        filename: str | None,
        content_type: str | None,
    ) -> DocumentResponse:

        # validate scenario exists
        scenario = await self._uow.scenario_repo.get_by_id(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")

        original_filename = filename or "file"
        safe = safe_upload_filename(original_filename)
        ext = Path(safe).suffix
        key = str(uuid7())
        raw_path_rel = f"scenarios/{scenario_id}/{key}{ext}"
        md_path_rel = f"scenarios/{scenario_id}/{key}.md"

        upload_root = Path(settings.UPLOAD_DIR)
        raw_dest = upload_root / raw_path_rel
        raw_dest.parent.mkdir(parents=True, exist_ok=True)
        raw_dest.write_bytes(file_content)

        try:
            md = MarkItDown()
            result = md.convert(str(raw_dest))
            markdown = getattr(result, "markdown", None) or getattr(
                result, "text_content", ""
            )
        except Exception as e:
            try:
                raw_dest.unlink(missing_ok=True)  # type: ignore[call-arg]
            except Exception:
                ...
            raise HTTPException(
                status_code=400,
                detail=f"Failed to convert file to markdown: {e}",
            )

        md_dest = upload_root / md_path_rel
        md_dest.parent.mkdir(parents=True, exist_ok=True)
        md_dest.write_text(markdown or "", encoding="utf-8")

        doc = await self._uow.document_repo.create(
            scenario_id=scenario_id,
            filename=original_filename,
            content_type=content_type,
            file_path=raw_path_rel,
            md_path=md_path_rel,
        )

        return DocumentResponse.model_validate(doc)
