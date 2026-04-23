from pydantic import BaseModel, Field


class ChunkTextRequest(BaseModel):
    text: str = Field(min_length=1)
    chunk_size: int = Field(default=512, gt=0)
    overlap: int = Field(default=64, ge=0)
