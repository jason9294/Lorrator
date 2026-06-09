import time
from logging import getLogger
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.realtime.websocket.manager import WebSocketConnectionManager
from app.core.realtime.websocket.envelopes import (
    DocumentsProcessUpdatedEnvelope,
    DocumentsProcessingStepUpdatedEnvelope,
)
from app.core.realtime.websocket.topics import WsTopic
from app.models import DocumentModel
from app.modules.document_pipeline.llm_recorder import PipelineLlmCallRecorder
from app.modules.document_pipeline.persistence import (
    PipelinePersistence,
    build_pending_steps,
)
from app.modules.document_pipeline.registry import DEFAULT_DOCUMENT_PIPELINE
from app.modules.document_pipeline.steps.base import PipelineStep
from app.modules.document_pipeline.types import PipelineContextState, PipelineOptions
from app.repositories.document_processing_llm_call_repo import (
    DocumentProcessingLlmCallRepository,
)
from app.repositories.document_processing_run_repo import DocumentProcessingRunRepository
from app.shared.enums import (
    DocumentStatus,
    ProcessingRunStatus,
    ProcessingStepStatus,
)

logger = getLogger(__name__)


class PipelineRunner:
    def __init__(
        self,
        *,
        session: AsyncSession,
        ws_manager: WebSocketConnectionManager,
        notify_user_id: UUID,
        scenario_id: UUID,
    ) -> None:
        self._session = session
        self._ws_manager = ws_manager
        self._notify_user_id = notify_user_id
        self._scenario_id = scenario_id
        self._repo = DocumentProcessingRunRepository(session)
        self._llm_call_repo = DocumentProcessingLlmCallRepository(session)
        self._persistence = PipelinePersistence(self._repo, self._llm_call_repo)

    async def run(
        self,
        *,
        document_id: UUID,
        graph_group_id: str,
        options: PipelineOptions,
    ) -> None:
        definition = DEFAULT_DOCUMENT_PIPELINE
        started_at = time.perf_counter()

        doc = await self._load_document(document_id)
        if doc is None:
            logger.warning(
                "Document not found, aborting pipeline document_id=%s scenario_id=%s",
                document_id,
                self._scenario_id,
            )
            return

        logger.info(
            "Starting pipeline document_id=%s scenario_id=%s pipeline_id=%s "
            "filename=%s clear_existing=%s legacy_untagged_chunks=%s",
            document_id,
            self._scenario_id,
            definition.pipeline_id,
            doc.filename,
            options.clear_existing,
            options.legacy_untagged_chunks,
        )

        ctx = PipelineContextState(
            document_id=document_id,
            scenario_id=self._scenario_id,
            graph_group_id=graph_group_id,
            filename=doc.filename,
            md_path=doc.md_path,
        )

        await self._persistence.initialize_run(
            document_id=document_id,
            pipeline_id=definition.pipeline_id,
            pending_steps=build_pending_steps(definition.steps),
        )
        logger.info(
            "Pipeline run initialized document_id=%s run_id=%s step_count=%s",
            document_id,
            self._persistence.run_id,
            len(definition.steps),
        )

        ctx.llm_recorder = PipelineLlmCallRecorder(
            repo=self._llm_call_repo,
            run_id=self._persistence.run_id,
        )

        await self._notify_document_status(
            document_id=document_id,
            status=DocumentStatus.PROCESSING,
        )

        try:
            for step in definition.steps:
                await self._run_step(step, ctx, options)

            total_ms = int((time.perf_counter() - started_at) * 1000)
            await self._persistence.finalize_run(
                status=ProcessingRunStatus.COMPLETED,
                total_duration_ms=total_ms,
            )
            doc.status = DocumentStatus.COMPLETED
            await self._session.commit()
            logger.info(
                "Pipeline completed document_id=%s run_id=%s total_duration_ms=%s",
                document_id,
                self._persistence.run_id,
                total_ms,
            )
            await self._notify_document_status(
                document_id=document_id,
                status=DocumentStatus.COMPLETED,
            )
        except Exception as exc:
            total_ms = int((time.perf_counter() - started_at) * 1000)
            await self._persistence.finalize_run(
                status=ProcessingRunStatus.FAILED,
                total_duration_ms=total_ms,
                error=str(exc),
            )
            doc.status = DocumentStatus.FAILED
            await self._session.commit()
            logger.exception(
                "Pipeline failed document_id=%s run_id=%s total_duration_ms=%s error=%s",
                document_id,
                self._persistence.run_id,
                total_ms,
                exc,
            )
            await self._notify_document_status(
                document_id=document_id,
                status=DocumentStatus.FAILED,
                error=str(exc),
            )

    async def _load_document(self, document_id: UUID) -> DocumentModel | None:
        result = await self._session.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        return result.scalar_one_or_none()

    async def _run_step(
        self,
        step: PipelineStep,
        ctx: PipelineContextState,
        options: PipelineOptions,
    ) -> None:
        step_id = step.id.value

        if not step.should_run(ctx, options):
            logger.info(
                "Step skipped document_id=%s step_id=%s title=%s",
                ctx.document_id,
                step_id,
                step.title,
            )
            await self._persistence.update_step(
                step_id,
                status=ProcessingStepStatus.SKIPPED.value,
                duration_ms=0,
                summary="此步驟已略過",
                result=None,
                error=None,
            )
            await self._notify_step_updated(step_id, ProcessingStepStatus.SKIPPED)
            return

        logger.info(
            "Step started document_id=%s step_id=%s title=%s",
            ctx.document_id,
            step_id,
            step.title,
        )
        await self._persistence.update_step(
            step_id,
            status=ProcessingStepStatus.RUNNING.value,
        )
        await self._notify_step_updated(step_id, ProcessingStepStatus.RUNNING)

        step_started = time.perf_counter()
        try:
            result: BaseModel = await step.execute(ctx, options)
            duration_ms = int((time.perf_counter() - step_started) * 1000)
            summary = step.build_summary(result)
            await self._persistence.update_step(
                step_id,
                status=ProcessingStepStatus.COMPLETED.value,
                duration_ms=duration_ms,
                summary=summary,
                result=result.model_dump(mode="json"),
                error=None,
            )
            await self._notify_step_updated(
                step_id,
                ProcessingStepStatus.COMPLETED,
                summary=summary,
            )
            logger.info(
                "Step completed document_id=%s step_id=%s duration_ms=%s summary=%s",
                ctx.document_id,
                step_id,
                duration_ms,
                summary,
            )
        except Exception as exc:
            duration_ms = int((time.perf_counter() - step_started) * 1000)
            logger.exception(
                "Step failed document_id=%s step_id=%s duration_ms=%s error=%s",
                ctx.document_id,
                step_id,
                duration_ms,
                exc,
            )
            await self._persistence.update_step(
                step_id,
                status=ProcessingStepStatus.FAILED.value,
                duration_ms=duration_ms,
                error=str(exc),
            )
            await self._notify_step_updated(
                step_id,
                ProcessingStepStatus.FAILED,
                error=str(exc),
            )
            raise
        finally:
            if ctx.llm_recorder is not None:
                await ctx.llm_recorder.flush()

    async def _notify_document_status(
        self,
        *,
        document_id: UUID,
        status: DocumentStatus,
        error: str | None = None,
    ) -> None:
        await self._ws_manager.send_to_topic(
            WsTopic.user_documents(self._notify_user_id),
            DocumentsProcessUpdatedEnvelope.for_document(
                document_id=document_id,
                scenario_id=self._scenario_id,
                status=status,
                error=error,
            ),
        )

    async def _notify_step_updated(
        self,
        step_id: str,
        status: ProcessingStepStatus,
        *,
        summary: str | None = None,
        error: str | None = None,
    ) -> None:
        await self._ws_manager.send_to_topic(
            WsTopic.user_documents(self._notify_user_id),
            DocumentsProcessingStepUpdatedEnvelope(
                document_id=str(self._persistence.document_id),
                run_id=str(self._persistence.run_id),
                step_id=step_id,
                status=status,
                summary=summary,
                error=error,
            ),
        )
