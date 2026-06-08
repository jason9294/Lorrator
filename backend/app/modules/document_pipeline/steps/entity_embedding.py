from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.graph import neo4j_driver
from app.db.sql import async_engine
from app.features.documents.services.helpers.entity_embedding import (
    embed_entities_and_build_similarity_edges,
)
from app.modules.document_pipeline.types import (
    EntityEmbeddingStepResult,
    PipelineContextState,
    PipelineOptions,
)
from app.modules.embedding import EMBEDDING_MODEL_KEY
from app.repositories.graph_repo import GraphRepo
from app.shared.enums import ProcessingStepId


class EntityEmbeddingStep:
    id = ProcessingStepId.ENTITY_EMBEDDING
    title = "實體向量化"
    description = "為實體名稱與描述建立 embedding，並計算實體間向量相似度"

    def should_run(self, ctx: PipelineContextState, options: PipelineOptions) -> bool:
        return bool(ctx.extractions)

    async def execute(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> EntityEmbeddingStepResult:
        if ctx.extractions is None:
            raise ValueError("Entity extraction results are not available")

        async with AsyncSession(async_engine) as sql_session:
            async with neo4j_driver.session() as graph_session:
                graph_repo = GraphRepo(graph_session)
                stats = await embed_entities_and_build_similarity_edges(
                    graph_repo,
                    sql_session,
                    ctx.extractions,
                    ctx.graph_group_id,
                )
                await sql_session.commit()

        return EntityEmbeddingStepResult(
            model_key=EMBEDDING_MODEL_KEY,
            entities_embedded=stats.entities_embedded,
            cache_hits=stats.cache_hits,
            cache_misses=stats.cache_misses,
            similarity_edges_created=stats.similarity_edges_created,
        )

    def build_summary(self, result: BaseModel) -> str:
        assert isinstance(result, EntityEmbeddingStepResult)
        return (
            f"向量化 {result.entities_embedded} 個實體 · "
            f"建立 {result.similarity_edges_created} 條相似度邊 · "
            f"快取命中 {result.cache_hits} / 未命中 {result.cache_misses}"
        )


entity_embedding_step = EntityEmbeddingStep()
