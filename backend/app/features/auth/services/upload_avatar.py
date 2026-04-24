from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile

from app.core.setting import get_settings
from app.db.uow import UnitOfWorkDependency

from ..schemas.responses import MeResponse

settings = get_settings()

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
_MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class UploadAvatarService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID, file: UploadFile) -> MeResponse:
        if file.content_type not in _ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type: {file.content_type}. Allowed: jpeg, png, webp, gif",
            )

        suffix = Path(file.filename or "avatar.jpg").suffix.lower()
        if suffix not in _ALLOWED_EXTENSIONS:
            suffix = ".jpg"

        content = await file.read()
        if len(content) > _MAX_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="Image must be smaller than 5 MB")

        upload_root = Path(settings.UPLOAD_DIR)
        avatar_dir = upload_root / "avatars"
        avatar_dir.mkdir(parents=True, exist_ok=True)

        dest = avatar_dir / f"{user_id}{suffix}"
        dest.write_bytes(content)

        avatar_url = f"/uploads/avatars/{user_id}{suffix}"

        user = await self._uow.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user = await self._uow.user_repo.update_profile(
            user=user,
            nickname=user.nickname,
            avatar_url=avatar_url,
        )

        return MeResponse(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
        )
