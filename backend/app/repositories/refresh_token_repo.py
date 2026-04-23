from datetime import timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlmodel import col

from app.models.refresh_token_model import RefreshTokenModel
from app.shared.utils import datetime_utcnow

from ._base_repo import BaseRepository


class RefreshTokenRepository(BaseRepository):
    async def create(
        self, user_id: UUID, hashed_validator: str, expires_in_days: int = 30
    ):
        token = RefreshTokenModel(
            user_id=user_id,
            validator_hash=hashed_validator,
            expires_at=datetime_utcnow() + timedelta(days=expires_in_days),
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_valid_token(self, token_id: UUID) -> RefreshTokenModel | None:
        """取得有效的 refresh token (未過期且未撤銷)"""
        stmt = select(RefreshTokenModel).where(
            col(RefreshTokenModel.id) == token_id,
            col(RefreshTokenModel.expires_at) > datetime_utcnow(),
            col(RefreshTokenModel.revoked) == False,  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_token(self, token_id: UUID):
        """撤銷 refresh token"""
        stmt = (
            update(RefreshTokenModel)
            .where(col(RefreshTokenModel.id) == token_id)
            .values(revoked=True)
        )
        await self.session.execute(stmt)


def provide_refresh_token_repo_cls() -> type[RefreshTokenRepository]:
    return RefreshTokenRepository
