from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from app.modules.document_pipeline.types import PipelineContextState, PipelineOptions
from app.shared.enums import ProcessingStepId


@runtime_checkable
class PipelineStep(Protocol):
    id: ProcessingStepId
    title: str
    description: str

    def should_run(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> bool: ...

    async def execute(
        self, ctx: PipelineContextState, options: PipelineOptions
    ) -> BaseModel: ...

    def build_summary(self, result: BaseModel) -> str: ...
