from neo4j import AsyncResult

from app.modules.rag.chunker import Chunk
from app.shared.enums import GraphRelationshipType

from ._base_graph_repo import BaseGraphRepo


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
