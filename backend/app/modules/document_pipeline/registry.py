from dataclasses import dataclass

from app.modules.document_pipeline.steps.base import PipelineStep
from app.modules.document_pipeline.steps.chunk import chunk_step
from app.modules.document_pipeline.steps.clear_graph import clear_graph_step
from app.modules.document_pipeline.steps.entity_embedding import entity_embedding_step
from app.modules.document_pipeline.steps.entity_extraction import entity_extraction_step
from app.modules.document_pipeline.steps.graph_build import graph_build_step
from app.modules.document_pipeline.steps.prepare import prepare_step

LORRATOR_DOCUMENT_PIPELINE_V1 = "lorrator_document_v1"


@dataclass(frozen=True)
class PipelineDefinition:
    pipeline_id: str
    steps: tuple[PipelineStep, ...]


DEFAULT_DOCUMENT_PIPELINE = PipelineDefinition(
    pipeline_id=LORRATOR_DOCUMENT_PIPELINE_V1,
    steps=(
        prepare_step,
        clear_graph_step,
        chunk_step,
        entity_extraction_step,
        graph_build_step,
        entity_embedding_step,
    ),
)
