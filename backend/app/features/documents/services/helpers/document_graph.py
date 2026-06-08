import asyncio
from uuid import UUID

from app.core import get_settings
from app.db.graph import neo4j_driver
from app.modules.document_pipeline.types import (
    ClearGraphStats,
    GraphBuildStats,
    GraphEdgeCreatedResult,
    GraphNodeCreatedResult,
)
from app.modules.rag.chunker import Chunk
from app.modules.rag.entity_extract import entity_extract
from app.modules.rag.json_schema import ExtractedEntities
from app.repositories.graph_repo import GraphRepo
from app.shared.utils import uuid7
from app.uncategorized.entity_types import NPC, Ending, Event, Item, Location
from graphiti_core import Graphiti
from graphiti_core.utils.datetime_utils import utc_now

settings = get_settings()


async def save_chunk_graph(
    repo: GraphRepo,
    *,
    chunk: Chunk,
    chunk_id: str,
    document_id: str,
    graph_group_id: str,
    extracted: ExtractedEntities,
) -> GraphBuildStats:
    stats = GraphBuildStats()
    stats.chunks_created = 1
    stats.nodes.append(
        GraphNodeCreatedResult(
            id=chunk_id,
            name=f"Chunk {chunk.index}",
            type="CHUNK",
            description=f"tokens [{chunk.start_token}:{chunk.end_token}]",
            source_chunk_index=chunk.index,
        )
    )

    await repo.create_chunk(
        chunk_id=chunk_id,
        document_id=document_id,
        graph_group_id=graph_group_id,
        chunk=chunk,
    )

    for entity in extracted.entities:
        was_created = not await repo.entity_exists(
            name=entity.name,
            graph_group_id=graph_group_id,
        )
        if was_created:
            stats.entities_created += 1
        else:
            stats.entities_merged += 1

        await repo.merge_entity_with_mention(
            name=entity.name,
            graph_group_id=graph_group_id,
            entity_type=entity.type,
            description=entity.description,
            chunk_id=chunk_id,
        )
        stats.nodes.append(
            GraphNodeCreatedResult(
                id=f"entity-{entity.name}-{chunk.index}",
                name=entity.name,
                type=entity.type,
                description=entity.description,
                source_chunk_index=chunk.index,
            )
        )
        stats.edges.append(
            GraphEdgeCreatedResult(
                id=f"mention-{chunk_id}-{entity.name}",
                source_name=f"Chunk {chunk.index}",
                target_name=entity.name,
                type="MENTION",
                description="chunk 提及此實體",
            )
        )

    for relationship in extracted.relationships:
        await repo.merge_entity_relationship(
            source_name=relationship.source_name,
            target_name=relationship.target_name,
            graph_group_id=graph_group_id,
            relationship_type=relationship.type,
            description=relationship.description,
        )
        stats.relationships_created += 1
        stats.edges.append(
            GraphEdgeCreatedResult(
                id=(
                    f"rel-{relationship.source_name}-"
                    f"{relationship.target_name}-{relationship.type}"
                ),
                source_name=relationship.source_name,
                target_name=relationship.target_name,
                type=relationship.type,
                description=relationship.description,
            )
        )

    return stats


async def clear_document_graph_data(
    graph_repo: GraphRepo,
    *,
    document_id: str,
    graph_group_id: str,
    legacy_untagged_chunks: bool = False,
) -> ClearGraphStats:
    stats = ClearGraphStats()
    stats.chunks_deleted = await graph_repo.delete_document_chunks(
        document_id=document_id,
        graph_group_id=graph_group_id,
    )

    if legacy_untagged_chunks:
        stats.legacy_chunks_deleted = await graph_repo.delete_legacy_untagged_chunks(
            graph_group_id=graph_group_id,
        )

    stats.orphan_entities_deleted = await graph_repo.delete_orphan_entities(
        graph_group_id=graph_group_id,
    )
    return stats


async def extract_with_graphiti(chunks: list[Chunk], graph_group_id: str) -> None:
    graphiti = Graphiti(
        settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD
    )
    try:
        await graphiti.build_indices_and_constraints()
        for i, chunk in enumerate(chunks):
            await graphiti.add_episode(
                name=f"TRPG Scenario {i}",
                episode_body=chunk.text,
                source_description="TRPG Scenario Chunk",
                reference_time=utc_now(),
                group_id=graph_group_id,
                entity_types={
                    "NPC": NPC,
                    "Event": Event,
                    "Location": Location,
                    "Item": Item,
                    "Ending": Ending,
                },
            )
    finally:
        await graphiti.close()


async def build_graph_from_extractions(
    chunks: list[Chunk],
    extractions: list[ExtractedEntities],
    graph_group_id: str,
    document_id: UUID,
) -> GraphBuildStats:
    if not chunks:
        return GraphBuildStats()

    document_id_str = str(document_id)
    combined = GraphBuildStats()
    async with neo4j_driver.session() as session:
        repo = GraphRepo(session)
        for chunk, extracted in zip(chunks, extractions, strict=True):
            chunk_stats = await save_chunk_graph(
                repo,
                chunk=chunk,
                chunk_id=str(uuid7()),
                document_id=document_id_str,
                graph_group_id=graph_group_id,
                extracted=extracted,
            )
            combined.chunks_created += chunk_stats.chunks_created
            combined.entities_created += chunk_stats.entities_created
            combined.entities_merged += chunk_stats.entities_merged
            combined.relationships_created += chunk_stats.relationships_created
            combined.nodes.extend(chunk_stats.nodes)
            combined.edges.extend(chunk_stats.edges)

    return combined


async def extract_with_lorrator(
    chunks: list[Chunk],
    graph_group_id: str,
    document_id: UUID,
) -> GraphBuildStats:
    if not chunks:
        return GraphBuildStats()

    extractions = await asyncio.gather(
        *[entity_extract(chunk.text) for chunk in chunks]
    )

    return await build_graph_from_extractions(
        chunks, list(extractions), graph_group_id, document_id
    )
