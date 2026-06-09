from dataclasses import dataclass, field
from uuid import UUID

from app.modules.document_pipeline.llm_recorder import LlmCallRecorder
from app.modules.document_pipeline.types import (
    EntityGroupingInputChunkResult,
    EntityGroupingInputEntityResult,
    EntityGroupingIterationResult,
    EntityGroupingMergeRecord,
    EntityGroupingStepResult,
)
from app.shared.enums import ProcessingStepId
from app.modules.rag.entity_grouper import entity_group
from app.modules.rag.json_schema import EntityGroupChunk, EntityGroupEntity
from app.repositories.graph_repo import GraphRepo


@dataclass
class EntityGroupingStats:
    total_iterations: int = 0
    total_merges: int = 0
    iterations: list[EntityGroupingIterationResult] = field(default_factory=list)


def _format_description(description: str | list[str]) -> str:
    if isinstance(description, list):
        return " / ".join(item for item in description if item)
    return description or ""


async def run_entity_grouping(
    graph_repo: GraphRepo,
    *,
    graph_group_id: str,
    document_id: UUID,
    llm_recorder: LlmCallRecorder | None = None,
) -> EntityGroupingStats:
    stats = EntityGroupingStats()
    iteration = 0

    while await graph_repo.has_similarity_edges(graph_group_id=graph_group_id):
        seed = await graph_repo.get_entity_with_most_similar_edges(
            graph_group_id=graph_group_id
        )
        if seed is None:
            break

        candidate_names = await graph_repo.get_similar_entity_cluster(
            seed_name=seed.name,
            graph_group_id=graph_group_id,
        )
        if len(candidate_names) < 2:
            break

        entities = await graph_repo.get_entities_for_grouping(
            names=candidate_names,
            graph_group_id=graph_group_id,
            document_id=str(document_id),
        )
        chunks = await graph_repo.get_chunks_for_entities(
            names=candidate_names,
            graph_group_id=graph_group_id,
            document_id=str(document_id),
        )

        chunk_id_by_real_id = {
            chunk.id: f"c{index}" for index, chunk in enumerate(chunks, start=1)
        }
        entity_id_by_name = {
            entity.name: f"e{index}" for index, entity in enumerate(entities, start=1)
        }
        name_by_entity_id = {
            temp_id: name for name, temp_id in entity_id_by_name.items()
        }

        llm_chunks = [
            EntityGroupChunk(
                chunk_id=chunk_id_by_real_id[chunk.id],
                content=chunk.content,
            )
            for chunk in chunks
        ]
        llm_entities = [
            EntityGroupEntity(
                entity_id=entity_id_by_name[entity.name],
                chunk_id=chunk_id_by_real_id.get(
                    entity.primary_chunk_id,
                    next(iter(chunk_id_by_real_id.values()), "c1"),
                ),
                name=entity.name,
                description=_format_description(entity.description),
            )
            for entity in entities
        ]

        iteration += 1
        grouping = await entity_group(
            llm_chunks,
            llm_entities,
            recorder=llm_recorder,
            step_id=ProcessingStepId.ENTITY_GROUPING.value,
            iteration=iteration,
        )
        resolved_groups = [
            [name_by_entity_id[temp_id] for temp_id in group if temp_id in name_by_entity_id]
            for group in grouping.entity_groups
        ]
        resolved_groups = [group for group in resolved_groups if group]
        grouped_names = {name for group in resolved_groups for name in group}
        for name in candidate_names:
            if name not in grouped_names:
                resolved_groups.append([name])

        for left_index, left_group in enumerate(resolved_groups):
            for right_group in resolved_groups[left_index + 1 :]:
                await graph_repo.delete_similarity_edges_between(
                    left_names=left_group,
                    right_names=right_group,
                    graph_group_id=graph_group_id,
                )

        merge_records: list[EntityGroupingMergeRecord] = []
        for group in resolved_groups:
            if len(group) < 2:
                continue

            target_name = seed.name if seed.name in group else group[0]
            source_names = [name for name in group if name != target_name]
            for source_name in source_names:
                source_entity = next(
                    (entity for entity in entities if entity.name == source_name),
                    None,
                )
                await graph_repo.merge_entity_into(
                    target_name=target_name,
                    source_name=source_name,
                    graph_group_id=graph_group_id,
                )
                stats.total_merges += 1
                merge_records.append(
                    EntityGroupingMergeRecord(
                        target_name=target_name,
                        source_name=source_name,
                        source_chunk_index=(
                            min(source_entity.chunk_indices)
                            if source_entity and source_entity.chunk_indices
                            else -1
                        ),
                        source_description=(
                            _format_description(source_entity.description)
                            if source_entity
                            else ""
                        ),
                        aliases_added=[source_name],
                    )
                )

        stats.total_iterations = iteration
        stats.iterations.append(
            EntityGroupingIterationResult(
                iteration=iteration,
                seed_name=seed.name,
                seed_similarity_degree=seed.degree,
                input_entities=[
                    EntityGroupingInputEntityResult(
                        temp_id=entity_id_by_name[entity.name],
                        name=entity.name,
                        chunk_index=(
                            min(entity.chunk_indices) if entity.chunk_indices else -1
                        ),
                        description=_format_description(entity.description),
                    )
                    for entity in entities
                ],
                input_chunks=[
                    EntityGroupingInputChunkResult(
                        temp_id=chunk_id_by_real_id[chunk.id],
                        chunk_index=chunk.index,
                        content=chunk.content,
                    )
                    for chunk in chunks
                ],
                llm_groups=[
                    [temp_id for temp_id in group if temp_id in name_by_entity_id]
                    for group in grouping.entity_groups
                ],
                merges=merge_records,
            )
        )

    return stats


def build_entity_grouping_step_result(stats: EntityGroupingStats) -> EntityGroupingStepResult:
    return EntityGroupingStepResult(
        total_iterations=stats.total_iterations,
        total_merges=stats.total_merges,
        iterations=stats.iterations,
    )
