import asyncio
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException

from app.core import get_settings
from app.db.uow import UnitOfWorkDependency
from app.modules.rag.chunker import chunk_text
from app.modules.rag.entity_extract import entity_extract
from app.modules.rag.json_schema import ExtractedEntities
from app.uncategorized.entity_types import Ending, Event, Item, Location
from graphiti_core import Graphiti
from graphiti_core.utils.datetime_utils import utc_now

from ..schemas.responses import ProcessDocumentResponse

settings = get_settings()


class ProcessDocumentService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, document_id: UUID) -> ProcessDocumentResponse:
        doc = await self._uow.document_repo.get_by_id(document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")

        # get document content
        upload_root = Path(settings.UPLOAD_DIR)
        path = upload_root / doc.md_path
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # chunk document
        chunks = chunk_text(content)

        # entities extraction
        # tasks = await asyncio.gather(*[entity_extract(chunk.text) for chunk in chunks])

        # Initialize Graphiti with Neo4j connection
        graphiti = Graphiti(
            settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD
        )

        try:
            # Initialize the graph database with graphiti's indices. This only needs to be done once.
            await graphiti.build_indices_and_constraints()

            # entities extraction
            for i, chunk in enumerate(chunks):
                await graphiti.add_episode(
                    name=f"TRPG Scenario {i}",
                    episode_body=chunk.text,
                    source_description="TRPG Scenario Chunk",
                    reference_time=utc_now(),
                    entity_types={
                        "Event": Event,
                        "Location": Location,
                        "Item": Item,
                        "Ending": Ending,
                    },
                )

        finally:
            # Close the connection
            await graphiti.close()

        result = ExtractedEntities(
            entities=[],
            relationships=[],
        )

        # for task in tasks:
        #     result.entities.extend(task.entities)
        #     result.relationships.extend(task.relationships)

        return ProcessDocumentResponse(
            document_id=document_id,
            entities=result.entities,
            relationships=result.relationships,
        )
