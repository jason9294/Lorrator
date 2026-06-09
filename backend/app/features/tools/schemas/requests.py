from pydantic import BaseModel, Field

from app.modules.rag.json_schema import EntityGroupChunk, EntityGroupEntity


class ChunkTextRequest(BaseModel):
    text: str = Field(min_length=1)
    chunk_size: int = Field(default=512, gt=0)
    overlap: int = Field(default=64, ge=0)


class EntityGroupRequest(BaseModel):
    chunks: list[EntityGroupChunk] = Field(min_length=1)
    entities: list[EntityGroupEntity] = Field(min_length=1)
