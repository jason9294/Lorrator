from datetime import datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.document_pipeline.types import (
    ChunkStepResult,
    ClearGraphStepResult,
    EntityEmbeddingStepResult,
    EntityExtractionStepResult,
    EntityGroupingStepResult,
    GraphBuildStepResult,
    PrepareStepResult,
)
from app.shared.enums import ProcessingStepId, ProcessingStepStatus


class ProcessingStepBaseResponse(BaseModel):
    title: str
    description: str
    status: ProcessingStepStatus
    duration_ms: int = 0
    summary: str | None = None
    error: str | None = None


class PrepareStepResponse(ProcessingStepBaseResponse):
    id: Literal[ProcessingStepId.PREPARE] = ProcessingStepId.PREPARE
    result: PrepareStepResult | None = None


class ClearGraphStepResponse(ProcessingStepBaseResponse):
    id: Literal[ProcessingStepId.CLEAR_GRAPH] = ProcessingStepId.CLEAR_GRAPH
    result: ClearGraphStepResult | None = None


class ChunkStepResponse(ProcessingStepBaseResponse):
    id: Literal[ProcessingStepId.CHUNK] = ProcessingStepId.CHUNK
    result: ChunkStepResult | None = None


class EntityExtractionStepResponse(ProcessingStepBaseResponse):
    id: Literal[ProcessingStepId.ENTITY_EXTRACTION] = ProcessingStepId.ENTITY_EXTRACTION
    result: EntityExtractionStepResult | None = None


class GraphBuildStepResponse(ProcessingStepBaseResponse):
    id: Literal[ProcessingStepId.GRAPH_BUILD] = ProcessingStepId.GRAPH_BUILD
    result: GraphBuildStepResult | None = None


class EntityEmbeddingStepResponse(ProcessingStepBaseResponse):
    id: Literal[ProcessingStepId.ENTITY_EMBEDDING] = ProcessingStepId.ENTITY_EMBEDDING
    result: EntityEmbeddingStepResult | None = None


class EntityGroupingStepResponse(ProcessingStepBaseResponse):
    id: Literal[ProcessingStepId.ENTITY_GROUPING] = ProcessingStepId.ENTITY_GROUPING
    result: EntityGroupingStepResult | None = None


ProcessingStepResponse = Annotated[
    PrepareStepResponse
    | ClearGraphStepResponse
    | ChunkStepResponse
    | EntityExtractionStepResponse
    | GraphBuildStepResponse
    | EntityEmbeddingStepResponse
    | EntityGroupingStepResponse,
    Field(discriminator="id"),
]


class DocumentProcessingLlmCallResponse(BaseModel):
    id: UUID
    step_id: ProcessingStepId
    call_key: str
    label: str
    model: str
    request: list[dict[str, Any]]
    response: dict[str, Any] | str
    sequence: int


class DocumentProcessingPipelineResponse(BaseModel):
    document_id: UUID
    filename: str
    started_at: datetime
    completed_at: datetime | None
    total_duration_ms: int | None
    steps: list[ProcessingStepResponse]
    llm_calls: list[DocumentProcessingLlmCallResponse] = []
