from dataclasses import dataclass

from neo4j import AsyncResult

from app.modules.rag.chunker import Chunk
from app.shared.enums import GraphRelationshipType

from ._base_graph_repo import BaseGraphRepo


@dataclass(frozen=True)
class EntitySimilaritySeed:
    name: str
    degree: int


@dataclass(frozen=True)
class EntityGroupingContext:
    name: str
    entity_type: str
    description: str | list[str]
    chunk_indices: list[int]
    primary_chunk_id: str


@dataclass(frozen=True)
class EntitySourceChunk:
    id: str
    index: int
    content: str


class GraphRepo(BaseGraphRepo):
    async def create_chunk(
        self,
        *,
        chunk_id: str,
        document_id: str,
        graph_group_id: str,
        chunk: Chunk,
    ) -> None:
        await self.session.run(
            """
            CREATE (c:Chunk {
                name: $name,
                id: $id,
                document_id: $document_id,
                group_id: $group_id,
                index: $index,
                content: $content,
                start_token: $start_token,
                end_token: $end_token,
                token_count: $token_count
            })
            """,
            name=f"Chunk {chunk.index}",
            id=chunk_id,
            document_id=document_id,
            group_id=graph_group_id,
            index=chunk.index,
            content=chunk.text,
            start_token=chunk.start_token,
            end_token=chunk.end_token,
            token_count=chunk.token_count,
        )

    async def entity_exists(self, *, name: str, graph_group_id: str) -> bool:
        result = await self.session.run(
            """
            MATCH (e:Entity {name: $name, group_id: $group_id})
            RETURN e LIMIT 1
            """,
            name=name,
            group_id=graph_group_id,
        )
        return await result.single() is not None

    async def merge_entity_with_mention(
        self,
        *,
        name: str,
        graph_group_id: str,
        entity_type: str,
        description: str,
        chunk_id: str,
    ) -> None:
        await self.session.run(
            """
            MERGE (e:Entity {name: $name, group_id: $group_id})
            ON CREATE SET
                e.type = $type,
                e.description = $description
            WITH e
            MATCH (c:Chunk {id: $chunk_id})
            MERGE (c)-[:MENTION]->(e)
            """,
            name=name,
            group_id=graph_group_id,
            type=entity_type,
            description=description,
            chunk_id=chunk_id,
        )

    async def merge_entity_relationship(
        self,
        *,
        source_name: str,
        target_name: str,
        graph_group_id: str,
        relationship_type: str,
        description: str,
    ) -> None:
        await self.session.run(
            """
            MERGE (a:Entity {name: $source_name, group_id: $group_id})
            ON CREATE SET a.type = 'Other', a.description = ''
            MERGE (b:Entity {name: $target_name, group_id: $group_id})
            ON CREATE SET b.type = 'Other', b.description = ''
            MERGE (a)-[r:RELATES_TO {type: $type}]->(b)
            SET r.description = $description
            """,
            source_name=source_name,
            target_name=target_name,
            group_id=graph_group_id,
            type=relationship_type,
            description=description,
        )

    async def set_entity_vectors(
        self,
        *,
        name: str,
        graph_group_id: str,
        name_vector: list[float],
        desc_vector: list[float],
    ) -> None:
        await self.session.run(
            """
            MATCH (e:Entity {name: $name, group_id: $group_id})
            SET e.name_vector = $name_vector,
                e.desc_vector = $desc_vector
            """,
            name=name,
            group_id=graph_group_id,
            name_vector=name_vector,
            desc_vector=desc_vector,
        )

    async def merge_similarity_edge(
        self,
        *,
        source_name: str,
        target_name: str,
        graph_group_id: str,
        name_similarity: float,
        desc_similarity: float,
        similarity: float,
    ) -> None:
        left_name, right_name = sorted((source_name, target_name))
        await self.session.run(
            """
            MATCH (a:Entity {name: $left_name, group_id: $group_id})
            MATCH (b:Entity {name: $right_name, group_id: $group_id})
            MERGE (a)-[r:SIMILAR_TO]->(b)
            SET r.name_similarity = $name_similarity,
                r.desc_similarity = $desc_similarity,
                r.similarity = $similarity
            """,
            left_name=left_name,
            right_name=right_name,
            group_id=graph_group_id,
            name_similarity=name_similarity,
            desc_similarity=desc_similarity,
            similarity=similarity,
        )

    async def delete_document_chunks(
        self, *, document_id: str, graph_group_id: str
    ) -> int:
        result = await self.session.run(
            """
            MATCH (c:Chunk {document_id: $document_id, group_id: $group_id})
            WITH collect(c) AS chunks, count(c) AS cnt
            FOREACH (node IN chunks | DETACH DELETE node)
            RETURN cnt AS deleted
            """,
            document_id=document_id,
            group_id=graph_group_id,
        )
        return await self._deleted_count(result)

    async def delete_legacy_untagged_chunks(self, *, graph_group_id: str) -> int:
        result = await self.session.run(
            """
            MATCH (c:Chunk {group_id: $group_id})
            WHERE c.document_id IS NULL
            WITH collect(c) AS chunks, count(c) AS cnt
            FOREACH (node IN chunks | DETACH DELETE node)
            RETURN cnt AS deleted
            """,
            group_id=graph_group_id,
        )
        return await self._deleted_count(result)

    async def delete_orphan_entities(self, *, graph_group_id: str) -> int:
        result = await self.session.run(
            """
            MATCH (e:Entity {group_id: $group_id})
            WHERE NOT (e)<-[:MENTION]-(:Chunk)
            WITH collect(e) AS entities, count(e) AS cnt
            FOREACH (node IN entities | DETACH DELETE node)
            RETURN cnt AS deleted
            """,
            group_id=graph_group_id,
        )
        return await self._deleted_count(result)

    async def has_similarity_edges(self, *, graph_group_id: str) -> bool:
        result = await self.session.run(
            """
            MATCH (a:Entity {group_id: $group_id})-[:SIMILAR_TO]-(b:Entity {group_id: $group_id})
            RETURN true AS exists
            LIMIT 1
            """,
            group_id=graph_group_id,
        )
        return await result.single() is not None

    async def get_entity_with_most_similar_edges(
        self, *, graph_group_id: str
    ) -> EntitySimilaritySeed | None:
        result = await self.session.run(
            """
            MATCH (e:Entity {group_id: $group_id})-[r:SIMILAR_TO]-(:Entity {group_id: $group_id})
            WITH e, count(r) AS degree
            ORDER BY degree DESC, e.name ASC
            LIMIT 1
            RETURN e.name AS name, degree
            """,
            group_id=graph_group_id,
        )
        record = await result.single()
        if record is None:
            return None
        return EntitySimilaritySeed(name=record["name"], degree=int(record["degree"]))

    async def get_similar_entity_cluster(
        self, *, seed_name: str, graph_group_id: str
    ) -> list[str]:
        result = await self.session.run(
            """
            MATCH (seed:Entity {name: $seed_name, group_id: $group_id})
            OPTIONAL MATCH (seed)-[:SIMILAR_TO]-(other:Entity {group_id: $group_id})
            WITH collect(DISTINCT other.name) AS neighbors, seed.name AS seed_name
            RETURN [seed_name] + neighbors AS names
            """,
            seed_name=seed_name,
            group_id=graph_group_id,
        )
        record = await result.single()
        if record is None:
            return []
        names = [name for name in record["names"] if name]
        return sorted(set(names), key=lambda name: (name != seed_name, name))

    async def get_entities_for_grouping(
        self,
        *,
        names: list[str],
        graph_group_id: str,
        document_id: str,
    ) -> list[EntityGroupingContext]:
        result = await self.session.run(
            """
            MATCH (e:Entity {group_id: $group_id})
            WHERE e.name IN $names
            OPTIONAL MATCH (c:Chunk {document_id: $document_id, group_id: $group_id})
              -[:MENTION]->(e)
            WITH e,
                 collect(DISTINCT c.index) AS chunk_indices,
                 collect(DISTINCT c.id) AS chunk_ids
            RETURN e.name AS name,
                   e.type AS entity_type,
                   e.description AS description,
                   [idx IN chunk_indices WHERE idx IS NOT NULL] AS chunk_indices,
                   [cid IN chunk_ids WHERE cid IS NOT NULL] AS chunk_ids
            """,
            names=names,
            group_id=graph_group_id,
            document_id=document_id,
        )
        entities: list[EntityGroupingContext] = []
        async for record in result:
            chunk_indices = sorted(int(index) for index in record["chunk_indices"])
            chunk_ids = list(record["chunk_ids"])
            entities.append(
                EntityGroupingContext(
                    name=record["name"],
                    entity_type=record["entity_type"] or "Other",
                    description=record["description"] or "",
                    chunk_indices=chunk_indices,
                    primary_chunk_id=chunk_ids[0] if chunk_ids else "",
                )
            )
        entities.sort(
            key=lambda entity: (
                min(entity.chunk_indices) if entity.chunk_indices else 10**9,
                entity.name,
            )
        )
        return entities

    async def get_chunks_for_entities(
        self,
        *,
        names: list[str],
        graph_group_id: str,
        document_id: str,
    ) -> list[EntitySourceChunk]:
        result = await self.session.run(
            """
            MATCH (e:Entity {group_id: $group_id})
            WHERE e.name IN $names
            MATCH (c:Chunk {document_id: $document_id, group_id: $group_id})
              -[:MENTION]->(e)
            RETURN DISTINCT c.id AS id, c.index AS index, c.content AS content
            ORDER BY c.index ASC
            """,
            names=names,
            group_id=graph_group_id,
            document_id=document_id,
        )
        chunks: list[EntitySourceChunk] = []
        async for record in result:
            chunks.append(
                EntitySourceChunk(
                    id=record["id"],
                    index=int(record["index"]),
                    content=record["content"] or "",
                )
            )
        return chunks

    async def delete_similarity_edges_between(
        self,
        *,
        left_names: list[str],
        right_names: list[str],
        graph_group_id: str,
    ) -> int:
        result = await self.session.run(
            """
            MATCH (a:Entity {group_id: $group_id})-[r:SIMILAR_TO]-(b:Entity {group_id: $group_id})
            WHERE a.name IN $left_names AND b.name IN $right_names
            DELETE r
            RETURN count(r) AS deleted
            """,
            left_names=left_names,
            right_names=right_names,
            group_id=graph_group_id,
        )
        return await self._deleted_count(result)

    async def delete_similarity_edge(
        self,
        *,
        source_name: str,
        target_name: str,
        graph_group_id: str,
    ) -> None:
        left_name, right_name = sorted((source_name, target_name))
        await self.session.run(
            """
            MATCH (a:Entity {name: $left_name, group_id: $group_id})
            MATCH (b:Entity {name: $right_name, group_id: $group_id})
            MATCH (a)-[r:SIMILAR_TO]-(b)
            DELETE r
            """,
            left_name=left_name,
            right_name=right_name,
            group_id=graph_group_id,
        )

    async def merge_entity_into(
        self,
        *,
        target_name: str,
        source_name: str,
        graph_group_id: str,
    ) -> None:
        if target_name == source_name:
            return

        target_props = await self._load_entity_properties(
            name=target_name,
            graph_group_id=graph_group_id,
        )
        source_props = await self._load_entity_properties(
            name=source_name,
            graph_group_id=graph_group_id,
        )
        if target_props is None or source_props is None:
            raise ValueError(
                f"Cannot merge entities: target={target_name}, source={source_name}"
            )

        merged_description = _merge_descriptions(
            target_props["description"],
            source_props["description"],
        )
        merged_aliases = _merge_aliases(
            target_props.get("alias"),
            source_name,
        )

        await self.session.run(
            """
            MATCH (target:Entity {name: $target_name, group_id: $group_id})
            SET target.description = $description,
                target.alias = $alias
            """,
            target_name=target_name,
            group_id=graph_group_id,
            description=merged_description,
            alias=merged_aliases,
        )

        await self.delete_similarity_edge(
            source_name=target_name,
            target_name=source_name,
            graph_group_id=graph_group_id,
        )

        await self.session.run(
            """
            MATCH (target:Entity {name: $target_name, group_id: $group_id})
            MATCH (source:Entity {name: $source_name, group_id: $group_id})
            MATCH (c:Chunk)-[m:MENTION]->(source)
            MERGE (c)-[:MENTION]->(target)
            DELETE m
            """,
            target_name=target_name,
            source_name=source_name,
            group_id=graph_group_id,
        )

        await self.session.run(
            """
            MATCH (source:Entity {name: $source_name, group_id: $group_id})
              -[r:RELATES_TO]->(other:Entity {group_id: $group_id})
            WHERE other.name <> $source_name
            MATCH (target:Entity {name: $target_name, group_id: $group_id})
            MERGE (target)-[nr:RELATES_TO {type: r.type}]->(other)
            SET nr.description = coalesce(nr.description, r.description)
            DELETE r
            """,
            target_name=target_name,
            source_name=source_name,
            group_id=graph_group_id,
        )

        await self.session.run(
            """
            MATCH (other:Entity {group_id: $group_id})
              -[r:RELATES_TO]->(source:Entity {name: $source_name, group_id: $group_id})
            WHERE other.name <> $source_name
            MATCH (target:Entity {name: $target_name, group_id: $group_id})
            MERGE (other)-[nr:RELATES_TO {type: r.type}]->(target)
            SET nr.description = coalesce(nr.description, r.description)
            DELETE r
            """,
            target_name=target_name,
            source_name=source_name,
            group_id=graph_group_id,
        )

        await self._migrate_similarity_edges(
            target_name=target_name,
            source_name=source_name,
            graph_group_id=graph_group_id,
        )

        await self.session.run(
            """
            MATCH (source:Entity {name: $source_name, group_id: $group_id})
            DETACH DELETE source
            """,
            source_name=source_name,
            group_id=graph_group_id,
        )

    async def _load_entity_properties(
        self, *, name: str, graph_group_id: str
    ) -> dict | None:
        result = await self.session.run(
            """
            MATCH (e:Entity {name: $name, group_id: $group_id})
            RETURN e.description AS description, e.alias AS alias
            """,
            name=name,
            group_id=graph_group_id,
        )
        record = await result.single()
        return dict(record) if record else None

    async def _migrate_similarity_edges(
        self,
        *,
        target_name: str,
        source_name: str,
        graph_group_id: str,
    ) -> None:
        result = await self.session.run(
            """
            MATCH (source:Entity {name: $source_name, group_id: $group_id})
              -[r:SIMILAR_TO]-(other:Entity {group_id: $group_id})
            WHERE other.name <> $target_name
            RETURN other.name AS other_name,
                   r.name_similarity AS name_similarity,
                   r.desc_similarity AS desc_similarity,
                   r.similarity AS similarity
            """,
            source_name=source_name,
            target_name=target_name,
            group_id=graph_group_id,
        )
        edges: list[dict] = [dict(record) async for record in result]
        for edge in edges:
            await self.merge_similarity_edge(
                source_name=target_name,
                target_name=edge["other_name"],
                graph_group_id=graph_group_id,
                name_similarity=float(edge["name_similarity"] or 0),
                desc_similarity=float(edge["desc_similarity"] or 0),
                similarity=float(edge["similarity"] or 0),
            )
        await self.session.run(
            """
            MATCH (source:Entity {name: $source_name, group_id: $group_id})
              -[r:SIMILAR_TO]-(:Entity {group_id: $group_id})
            DELETE r
            """,
            source_name=source_name,
            group_id=graph_group_id,
        )

    async def query_scenario_graph(self, graph_group_id: str) -> AsyncResult:
        return await self.session.run(
            """
            MATCH (n)
            WHERE n.group_id = $group_id
            WITH collect(n) AS nodes

            UNWIND nodes AS n
            OPTIONAL MATCH (n)-[r]->(m)
            WHERE m IN nodes AND type(r) <> $similar_to_type

            RETURN DISTINCT n, r, m
            """,
            group_id=graph_group_id,
            similar_to_type=GraphRelationshipType.SIMILAR_TO,
        )

    @staticmethod
    async def _deleted_count(result: AsyncResult) -> int:
        record = await result.single()
        return int(record["deleted"]) if record else 0


def _normalize_description_list(description: str | list[str] | None) -> list[str]:
    if description is None:
        return []
    if isinstance(description, list):
        return [item for item in description if item]
    if description == "":
        return []
    return [description]


def _merge_descriptions(
    target_description: str | list[str] | None,
    source_description: str | list[str] | None,
) -> list[str]:
    merged: list[str] = []
    for item in _normalize_description_list(target_description):
        if item not in merged:
            merged.append(item)
    for item in _normalize_description_list(source_description):
        if item not in merged:
            merged.append(item)
    return merged


def _merge_aliases(existing_aliases: list[str] | None, source_name: str) -> list[str]:
    aliases = list(existing_aliases or [])
    if source_name not in aliases:
        aliases.append(source_name)
    return aliases
