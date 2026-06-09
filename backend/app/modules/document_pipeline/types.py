from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

from app.modules.rag.chunker import Chunk
from app.modules.rag.json_schema import ExtractedEntities

if TYPE_CHECKING:
    from app.modules.document_pipeline.llm_recorder import LlmCallRecorder


class PrepareStepResult(BaseModel):
    md_path: str
    character_count: int
    line_count: int
    preview: str


class ChunkItemResult(BaseModel):
    index: int
    start_token: int
    end_token: int
    token_count: int
    text: str


class ChunkStepResult(BaseModel):
    chunk_size: int
    overlap: int
    total_tokens: int
    chunks: list[ChunkItemResult]


class ExtractedEntityResult(BaseModel):
    name: str
    type: str
    description: str


class ExtractedRelationshipResult(BaseModel):
    source_name: str
    target_name: str
    type: str
    description: str


class ChunkExtractionResult(BaseModel):
    chunk_index: int
    entities: list[ExtractedEntityResult]
    relationships: list[ExtractedRelationshipResult]


class EntityExtractionStepResult(BaseModel):
    model: str
    chunk_results: list[ChunkExtractionResult]
    total_entities: int
    total_relationships: int


class EntityEmbeddingStepResult(BaseModel):
    model_key: str
    entities_embedded: int
    cache_hits: int
    cache_misses: int
    similarity_edges_created: int


class EntityGroupingInputEntityResult(BaseModel):
    temp_id: str
    name: str
    chunk_index: int
    description: str


class EntityGroupingInputChunkResult(BaseModel):
    temp_id: str
    chunk_index: int
    content: str


class EntityGroupingMergeRecord(BaseModel):
    target_name: str
    source_name: str
    source_chunk_index: int
    source_description: str
    aliases_added: list[str]


class EntityGroupingIterationResult(BaseModel):
    iteration: int
    seed_name: str
    seed_similarity_degree: int
    input_entities: list[EntityGroupingInputEntityResult]
    input_chunks: list[EntityGroupingInputChunkResult]
    llm_groups: list[list[str]]
    merges: list[EntityGroupingMergeRecord]


class EntityGroupingStepResult(BaseModel):
    total_iterations: int
    total_merges: int
    iterations: list[EntityGroupingIterationResult]


class GraphNodeCreatedResult(BaseModel):
    id: str
    name: str
    type: str
    description: str
    source_chunk_index: int


class GraphEdgeCreatedResult(BaseModel):
    id: str
    source_name: str
    target_name: str
    type: str
    description: str


class GraphBuildStepResult(BaseModel):
    chunks_created: int
    entities_created: int
    entities_merged: int
    relationships_created: int
    nodes: list[GraphNodeCreatedResult]
    edges: list[GraphEdgeCreatedResult]


class ClearGraphStepResult(BaseModel):
    chunks_deleted: int
    legacy_chunks_deleted: int
    orphan_entities_deleted: int


class ProcessingStepSnapshot(BaseModel):
    id: str
    title: str
    description: str
    status: str
    duration_ms: int = 0
    summary: str | None = None
    error: str | None = None
    result: dict | None = None


@dataclass
class GraphBuildStats:
    chunks_created: int = 0
    entities_created: int = 0
    entities_merged: int = 0
    relationships_created: int = 0
    nodes: list[GraphNodeCreatedResult] = field(default_factory=list)
    edges: list[GraphEdgeCreatedResult] = field(default_factory=list)


@dataclass
class ClearGraphStats:
    chunks_deleted: int = 0
    legacy_chunks_deleted: int = 0
    orphan_entities_deleted: int = 0


@dataclass
class PipelineContextState:
    document_id: UUID
    scenario_id: UUID
    graph_group_id: str
    filename: str
    md_path: str | None
    markdown_content: str | None = None
    chunks: list[Chunk] | None = None
    extractions: list[ExtractedEntities] | None = None
    graph_build_stats: GraphBuildStats | None = None
    clear_graph_stats: ClearGraphStats | None = None
    llm_recorder: "LlmCallRecorder | None" = None


class PipelineOptions(BaseModel):
    graph_group_id: str
    clear_existing: bool = False
    legacy_untagged_chunks: bool = False


DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64
MARKDOWN_PREVIEW_MAX_CHARS = 2000
ENTITY_EXTRACTION_MODEL = "gpt-5.4-mini"
