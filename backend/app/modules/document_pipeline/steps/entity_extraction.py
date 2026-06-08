import asyncio

from pydantic import BaseModel

from app.modules.document_pipeline.types import (
    ENTITY_EXTRACTION_MODEL,
    ChunkExtractionResult,
    EntityExtractionStepResult,
    ExtractedEntityResult,
    ExtractedRelationshipResult,
    PipelineContextState,
    PipelineOptions,
)
from app.modules.rag.entity_extract import entity_extract
from app.shared.enums import ProcessingStepId


class EntityExtractionStep:
    id = ProcessingStepId.ENTITY_EXTRACTION
    title = "實體抽取"
    description = "對每個 chunk 呼叫 LLM，抽取 NPC、地點、道具、事件與關係"

    def should_run(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> bool:
        return True

    async def execute(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> EntityExtractionStepResult:
        if not ctx.chunks:
            ctx.extractions = []
            return EntityExtractionStepResult(
                model=ENTITY_EXTRACTION_MODEL,
                chunk_results=[],
                total_entities=0,
                total_relationships=0,
            )

        extractions = await asyncio.gather(
            *[entity_extract(chunk.text) for chunk in ctx.chunks]
        )
        ctx.extractions = list(extractions)

        chunk_results: list[ChunkExtractionResult] = []
        total_entities = 0
        total_relationships = 0

        for chunk, extracted in zip(ctx.chunks, extractions, strict=True):
            entities = [
                ExtractedEntityResult(
                    name=entity.name,
                    type=entity.type,
                    description=entity.description,
                )
                for entity in extracted.entities
            ]
            relationships = [
                ExtractedRelationshipResult(
                    source_name=relationship.source_name,
                    target_name=relationship.target_name,
                    type=relationship.type,
                    description=relationship.description,
                )
                for relationship in extracted.relationships
            ]
            total_entities += len(entities)
            total_relationships += len(relationships)
            chunk_results.append(
                ChunkExtractionResult(
                    chunk_index=chunk.index,
                    entities=entities,
                    relationships=relationships,
                )
            )

        return EntityExtractionStepResult(
            model=ENTITY_EXTRACTION_MODEL,
            chunk_results=chunk_results,
            total_entities=total_entities,
            total_relationships=total_relationships,
        )

    def build_summary(self, result: BaseModel) -> str:
        assert isinstance(result, EntityExtractionStepResult)
        return (
            f"抽取 {result.total_entities} 個實體 · "
            f"{result.total_relationships} 條關係"
        )


entity_extraction_step = EntityExtractionStep()
