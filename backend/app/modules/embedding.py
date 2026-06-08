import math
from dataclasses import dataclass

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_settings
from app.repositories.embedding_cache_repo import EmbeddingCacheRepository
from app.shared.utils.text_hash import content_hash

settings = get_settings()

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_MODEL_KEY = f"{EMBEDDING_MODEL}:{settings.EMBEDDING_DIM}"


@dataclass
class EmbeddingCacheStats:
    hits: int = 0
    misses: int = 0


async def openai_embedding(openai_client: AsyncOpenAI, text: str) -> list[float]:
    response = await openai_client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL,
        dimensions=settings.EMBEDDING_DIM,
    )
    return response.data[0].embedding


def zero_vector() -> list[float]:
    return [0.0] * settings.EMBEDDING_DIM


def cosine_similarity(a: list[float], b: list[float]) -> float:
    # calculate the cosine similarity between two vectors
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


async def get_or_create_embedding(
    session: AsyncSession,
    openai_client: AsyncOpenAI,
    text: str,
    *,
    cache_stats: EmbeddingCacheStats | None = None,
) -> list[float]:
    normalized = text.strip()
    if not normalized:
        return zero_vector()

    digest = content_hash(normalized)
    repo = EmbeddingCacheRepository(session)
    cached = await repo.get(digest, EMBEDDING_MODEL_KEY)
    if cached is not None:
        if cache_stats is not None:
            cache_stats.hits += 1
        return list(cached.vector)

    vector = await openai_embedding(openai_client, normalized)
    await repo.upsert(
        content_hash=digest,
        model_key=EMBEDDING_MODEL_KEY,
        source_text=normalized,
        vector=vector,
    )
    if cache_stats is not None:
        cache_stats.misses += 1
    return vector
