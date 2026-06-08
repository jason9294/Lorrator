from pydantic import BaseModel

from app.features.documents.services.helpers.document_graph import build_graph_from_extractions
from app.modules.document_pipeline.types import (
    GraphBuildStepResult,
    PipelineContextState,
    PipelineOptions,
)
from app.shared.enums import ProcessingStepId


class GraphBuildStep:
    id = ProcessingStepId.GRAPH_BUILD
    title = "構建知識圖譜"
    description = "將 chunk、實體與關係寫入 Neo4j，建立 MENTION 與 RELATES_TO 邊"

    def should_run(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> bool:
        return True

    async def execute(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> GraphBuildStepResult:
        if ctx.extractions is None or ctx.chunks is None:
            raise ValueError("Entity extraction results are not available")

        stats = await build_graph_from_extractions(
            ctx.chunks,
            ctx.extractions,
            ctx.graph_group_id,
            ctx.document_id,
        )
        ctx.graph_build_stats = stats

        return GraphBuildStepResult(
            chunks_created=stats.chunks_created,
            entities_created=stats.entities_created,
            entities_merged=stats.entities_merged,
            relationships_created=stats.relationships_created,
            nodes=stats.nodes,
            edges=stats.edges,
        )

    def build_summary(self, result: BaseModel) -> str:
        assert isinstance(result, GraphBuildStepResult)
        return (
            f"建立 {result.chunks_created} 個 Chunk 節點 · "
            f"合併 {result.entities_merged} 個實體 · "
            f"{result.relationships_created} 條關係"
        )


graph_build_step = GraphBuildStep()
