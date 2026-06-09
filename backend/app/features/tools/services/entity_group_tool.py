from fastapi import HTTPException

from app.modules.rag.entity_grouper import entity_group
from app.modules.rag.json_schema import EntityGroupChunk, EntityGroupEntity


class EntityGroupToolService:
    async def execute(
        self,
        chunks: list[EntityGroupChunk],
        entities: list[EntityGroupEntity],
    ):
        try:
            return await entity_group(chunks, entities)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
