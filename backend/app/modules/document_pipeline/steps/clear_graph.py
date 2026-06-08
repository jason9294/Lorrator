from pydantic import BaseModel

from app.db.graph import neo4j_driver
from app.features.documents.services.helpers.document_graph import clear_document_graph_data
from app.modules.document_pipeline.types import (
    ClearGraphStepResult,
    PipelineContextState,
    PipelineOptions,
)
from app.repositories.graph_repo import GraphRepo
from app.shared.enums import ProcessingStepId


class ClearGraphStep:
    id = ProcessingStepId.CLEAR_GRAPH
    title = "清除舊圖譜"
    description = "重新處理前刪除該文件在 Neo4j 中的 chunk 與孤立實體"

    def should_run(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> bool:
        return options.clear_existing

    async def execute(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> ClearGraphStepResult:
        async with neo4j_driver.session() as session:
            repo = GraphRepo(session)
            stats = await clear_document_graph_data(
                repo,
                document_id=str(ctx.document_id),
                graph_group_id=ctx.graph_group_id,
                legacy_untagged_chunks=options.legacy_untagged_chunks,
            )
        ctx.clear_graph_stats = stats
        return ClearGraphStepResult(
            chunks_deleted=stats.chunks_deleted,
            legacy_chunks_deleted=stats.legacy_chunks_deleted,
            orphan_entities_deleted=stats.orphan_entities_deleted,
        )

    def build_summary(self, result: BaseModel) -> str:
        assert isinstance(result, ClearGraphStepResult)
        return (
            f"刪除 {result.chunks_deleted} 個 chunk · "
            f"{result.orphan_entities_deleted} 個孤立實體"
        )


clear_graph_step = ClearGraphStep()
