from pydantic import BaseModel

from app.modules.document_pipeline.types import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    ChunkItemResult,
    ChunkStepResult,
    PipelineContextState,
    PipelineOptions,
)
from app.modules.rag.chunker import chunk_text
from app.shared.enums import ProcessingStepId


class ChunkStep:
    id = ProcessingStepId.CHUNK
    title = "文本分塊"
    description = "依 token 長度切分文本，保留重疊窗口以維持語意連貫"

    def should_run(self, ctx: PipelineContextState, options: PipelineOptions) -> bool:
        return True

    async def execute(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> ChunkStepResult:
        if ctx.markdown_content is None:
            raise ValueError("Markdown content is not prepared")

        chunks = chunk_text(
            ctx.markdown_content,
            chunk_size=DEFAULT_CHUNK_SIZE,
            overlap=DEFAULT_CHUNK_OVERLAP,
        )
        ctx.chunks = chunks

        total_tokens = chunks[-1].end_token if chunks else 0
        return ChunkStepResult(
            chunk_size=DEFAULT_CHUNK_SIZE,
            overlap=DEFAULT_CHUNK_OVERLAP,
            total_tokens=total_tokens,
            chunks=[
                ChunkItemResult(
                    index=chunk.index,
                    start_token=chunk.start_token,
                    end_token=chunk.end_token,
                    token_count=chunk.token_count,
                    text=chunk.text,
                )
                for chunk in chunks
            ],
        )

    def build_summary(self, result: BaseModel) -> str:
        assert isinstance(result, ChunkStepResult)
        return (
            f"切分為 {len(result.chunks)} 個 chunk · 共 {result.total_tokens:,} tokens"
        )


chunk_step = ChunkStep()
