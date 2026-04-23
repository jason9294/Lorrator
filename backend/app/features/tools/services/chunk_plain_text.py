from fastapi import HTTPException

from app.modules.rag.chunker import chunk_text

from ..schemas.requests import ChunkTextRequest
from ..schemas.responses import ChunkResponse, ChunkTextResponse


class ChunkPlainTextService:
    async def execute(self, body: ChunkTextRequest) -> ChunkTextResponse:
        try:
            chunks = chunk_text(
                text=body.text,
                chunk_size=body.chunk_size,
                overlap=body.overlap,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return ChunkTextResponse(
            chunks=[
                ChunkResponse(
                    text=c.text,
                    start_token=c.start_token,
                    end_token=c.end_token,
                    token_count=c.token_count,
                    index=c.index,
                )
                for c in chunks
            ]
        )
