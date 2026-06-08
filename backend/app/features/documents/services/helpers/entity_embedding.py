from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.embedding import (
    EMBEDDING_MODEL_KEY,
    EmbeddingCacheStats,
    cosine_similarity,
    get_or_create_embedding,
)
from app.modules.rag.client import client as openai_client
from app.modules.rag.json_schema import ExtractedEntities
from app.repositories.graph_repo import GraphRepo


@dataclass
class EntityEmbeddingStats:
    model_key: str = EMBEDDING_MODEL_KEY
    entities_embedded: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    similarity_edges_created: int = 0


async def embed_entities_and_build_similarity_edges(
    graph_repo: GraphRepo,
    sql_session: AsyncSession,
    extractions: list[ExtractedEntities],
    graph_group_id: str,
) -> EntityEmbeddingStats:
    stats = EntityEmbeddingStats()
    cache_stats = EmbeddingCacheStats()

    entities_by_name: dict[str, tuple[str, str]] = {}
    for extracted in extractions:
        for entity in extracted.entities:
            entities_by_name[entity.name] = (entity.name, entity.description)

    if not entities_by_name:
        return stats

    embedded: list[tuple[str, list[float], list[float]]] = []
    for name, description in entities_by_name.values():
        name_vector = await get_or_create_embedding(
            sql_session,
            openai_client,
            name,
            cache_stats=cache_stats,
        )
        desc_vector = await get_or_create_embedding(
            sql_session,
            openai_client,
            description,
            cache_stats=cache_stats,
        )
        await graph_repo.set_entity_vectors(
            name=name,
            graph_group_id=graph_group_id,
            name_vector=name_vector,
            desc_vector=desc_vector,
        )
        embedded.append((name, name_vector, desc_vector))
        stats.entities_embedded += 1

    stats.cache_hits = cache_stats.hits
    stats.cache_misses = cache_stats.misses

    for i, (source_name, source_name_vector, source_desc_vector) in enumerate(embedded):
        for target_name, target_name_vector, target_desc_vector in embedded[i + 1 :]:
            name_similarity = cosine_similarity(source_name_vector, target_name_vector)
            desc_similarity = cosine_similarity(source_desc_vector, target_desc_vector)
            similarity = (name_similarity + desc_similarity) / 2.0

            # 大於一定相似度才建立 edge
            if similarity >= 0.5:
                # 使用 merge 避免建立重複的 edge
                await graph_repo.merge_similarity_edge(
                    source_name=source_name,
                    target_name=target_name,
                    graph_group_id=graph_group_id,
                    name_similarity=name_similarity,
                    desc_similarity=desc_similarity,
                    similarity=similarity,
                )
                stats.similarity_edges_created += 1

    return stats
