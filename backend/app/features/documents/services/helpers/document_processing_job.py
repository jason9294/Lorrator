from logging import getLogger
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.realtime import get_ws_connection_manager
from app.db.sql import async_engine
from app.modules.document_pipeline.runner import PipelineRunner
from app.modules.document_pipeline.types import PipelineOptions

logger = getLogger(__name__)


async def run_document_processing_job(
    *,
    document_id: UUID,
    scenario_id: UUID,
    graph_group_id: str,
    notify_user_id: UUID,
    clear_existing: bool = False,
    legacy_untagged_chunks: bool = False,
) -> None:
    logger.info(
        "Document processing job scheduled document_id=%s scenario_id=%s "
        "clear_existing=%s legacy_untagged_chunks=%s",
        document_id,
        scenario_id,
        clear_existing,
        legacy_untagged_chunks,
    )

    async with AsyncSession(async_engine) as session:
        runner = PipelineRunner(
            session=session,
            ws_manager=get_ws_connection_manager(),
            notify_user_id=notify_user_id,
            scenario_id=scenario_id,
        )
        await runner.run(
            document_id=document_id,
            graph_group_id=graph_group_id,
            options=PipelineOptions(
                graph_group_id=graph_group_id,
                clear_existing=clear_existing,
                legacy_untagged_chunks=legacy_untagged_chunks,
            ),
        )
