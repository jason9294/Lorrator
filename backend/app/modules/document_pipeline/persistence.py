from uuid import UUID

from sqlalchemy.orm.attributes import flag_modified

from app.models import DocumentProcessingRunModel
from app.modules.document_pipeline.types import ProcessingStepSnapshot
from app.repositories.document_processing_llm_call_repo import (
    DocumentProcessingLlmCallRepository,
)
from app.repositories.document_processing_run_repo import DocumentProcessingRunRepository
from app.shared.enums import ProcessingRunStatus, ProcessingStepStatus


def build_pending_steps(
    steps: tuple,
) -> list[dict]:
    snapshots: list[dict] = []
    for step in steps:
        snapshot = ProcessingStepSnapshot(
            id=step.id.value,
            title=step.title,
            description=step.description,
            status=ProcessingStepStatus.PENDING.value,
        )
        snapshots.append(snapshot.model_dump(mode="json"))
    return snapshots


class PipelinePersistence:
    def __init__(
        self,
        repo: DocumentProcessingRunRepository,
        llm_call_repo: DocumentProcessingLlmCallRepository,
    ) -> None:
        self._repo = repo
        self._llm_call_repo = llm_call_repo
        self._run: DocumentProcessingRunModel | None = None
        self._run_id: UUID | None = None
        self._document_id: UUID | None = None

    @property
    def run(self) -> DocumentProcessingRunModel:
        if self._run is None:
            raise RuntimeError("Pipeline run has not been initialized")
        return self._run

    @property
    def run_id(self) -> UUID:
        if self._run_id is None:
            raise RuntimeError("Pipeline run has not been initialized")
        return self._run_id

    @property
    def document_id(self) -> UUID:
        if self._document_id is None:
            raise RuntimeError("Pipeline run has not been initialized")
        return self._document_id

    async def initialize_run(
        self,
        *,
        document_id: UUID,
        pipeline_id: str,
        pending_steps: list[dict],
    ) -> DocumentProcessingRunModel:
        run = DocumentProcessingRunModel(
            document_id=document_id,
            pipeline_id=pipeline_id,
            status=ProcessingRunStatus.RUNNING,
            steps=pending_steps,
        )
        self._run = await self._repo.upsert(run)
        self._run_id = self._run.id
        self._document_id = document_id
        await self._llm_call_repo.delete_by_run_id(self._run.id)
        return self._run

    def _find_step_index(self, step_id: str) -> int:
        for index, step in enumerate(self.run.steps):
            if step.get("id") == step_id:
                return index
        raise KeyError(f"Step not found: {step_id}")

    async def update_step(self, step_id: str, **fields) -> None:
        index = self._find_step_index(step_id)
        updated = {**self.run.steps[index], **fields}
        self.run.steps[index] = updated
        flag_modified(self.run, "steps")
        await self._repo.session.flush()

    async def finalize_run(
        self,
        *,
        status: ProcessingRunStatus,
        total_duration_ms: int | None = None,
        error: str | None = None,
    ) -> None:
        from app.shared.utils import datetime_utcnow

        self.run.status = status
        self.run.total_duration_ms = total_duration_ms
        self.run.error = error
        if status in (ProcessingRunStatus.COMPLETED, ProcessingRunStatus.FAILED):
            self.run.completed_at = datetime_utcnow()
        await self._repo.session.flush()
