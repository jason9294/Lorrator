from pydantic import BaseModel


class ChunkResponse(BaseModel):
    text: str
    start_token: int
    end_token: int
    token_count: int
    index: int


class ChunkTextResponse(BaseModel):
    chunks: list[ChunkResponse]

