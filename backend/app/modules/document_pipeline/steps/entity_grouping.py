from pydantic import BaseModel

from app.db.graph import neo4j_driver
from app.features.documents.services.helpers.entity_grouping import (
    build_entity_grouping_step_result,
    run_entity_grouping,
)
from app.modules.document_pipeline.types import (
    EntityGroupingStepResult,
    PipelineContextState,
    PipelineOptions,
)
from app.repositories.graph_repo import GraphRepo
from app.shared.enums import ProcessingStepId


class EntityGroupingStep:
    id = ProcessingStepId.ENTITY_GROUPING
    title = "實體分群合併"
    description = "依 LLM 分群結果合併相似實體，並移除跨群相似邊"

    def should_run(self, ctx: PipelineContextState, options: PipelineOptions) -> bool:
        return bool(ctx.extractions)

    async def execute(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> EntityGroupingStepResult:
        async with neo4j_driver.session() as graph_session:
            graph_repo = GraphRepo(graph_session)
            stats = await run_entity_grouping(
                graph_repo,
                graph_group_id=ctx.graph_group_id,
                document_id=ctx.document_id,
            )

        return build_entity_grouping_step_result(stats)

    def build_summary(self, result: BaseModel) -> str:
        assert isinstance(result, EntityGroupingStepResult)
        if result.total_iterations == 0:
            return "無相似邊，略過實體分群"
        return (
            f"執行 {result.total_iterations} 輪分群 · "
            f"合併 {result.total_merges} 個實體"
        )


entity_grouping_step = EntityGroupingStep()
