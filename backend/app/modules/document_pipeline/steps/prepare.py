from pathlib import Path

from pydantic import BaseModel

from app.core import get_settings
from app.modules.document_pipeline.types import (
    MARKDOWN_PREVIEW_MAX_CHARS,
    PipelineContextState,
    PipelineOptions,
    PrepareStepResult,
)
from app.shared.enums import ProcessingStepId

settings = get_settings()


class PrepareStep:
    id = ProcessingStepId.PREPARE
    title = "讀取 Markdown"
    description = "從儲存位置載入轉換後的 Markdown 原文"

    def should_run(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> bool:
        return True

    async def execute(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> PrepareStepResult:
        if not ctx.md_path:
            raise ValueError("Document markdown path is missing")

        path = Path(settings.UPLOAD_DIR) / ctx.md_path
        if not path.exists():
            raise FileNotFoundError("Markdown file missing")

        content = path.read_text(encoding="utf-8")
        ctx.markdown_content = content

        preview = content
        if len(preview) > MARKDOWN_PREVIEW_MAX_CHARS:
            preview = preview[:MARKDOWN_PREVIEW_MAX_CHARS] + "…"

        return PrepareStepResult(
            md_path=ctx.md_path,
            character_count=len(content),
            line_count=content.count("\n") + (1 if content else 0),
            preview=preview,
        )

    def build_summary(self, result: BaseModel) -> str:
        assert isinstance(result, PrepareStepResult)
        return (
            f"成功讀取 {result.character_count:,} 字元 · {result.line_count} 行"
        )


prepare_step = PrepareStep()
