from fastapi import HTTPException

from app.modules.rag.entity_extract import entity_extract


class EntityExtractToolService:
    async def execute(self, text: str):
        try:
            return await entity_extract(text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
