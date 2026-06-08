from sqlmodel import select

from app.models import EmbeddingCacheModel

from ._base_repo import BaseRepository


class EmbeddingCacheRepository(BaseRepository):
    async def get(
        self, content_hash: str, model_key: str
    ) -> EmbeddingCacheModel | None:
        statement = select(EmbeddingCacheModel).where(
            EmbeddingCacheModel.content_hash == content_hash,
            EmbeddingCacheModel.model_key == model_key,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        *,
        content_hash: str,
        model_key: str,
        source_text: str,
        vector: list[float],
    ) -> EmbeddingCacheModel:
        existing = await self.get(content_hash, model_key)
        if existing is not None:
            existing.source_text = source_text
            existing.vector = vector
            await self.session.flush()
            return existing

        row = EmbeddingCacheModel(
            content_hash=content_hash,
            model_key=model_key,
            source_text=source_text,
            vector=vector,
        )
        self.session.add(row)
        await self.session.flush()
        return row
