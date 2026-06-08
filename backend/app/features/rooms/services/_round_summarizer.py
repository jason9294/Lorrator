import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from app.db.sql import async_engine
from app.models import RoomModel
from app.modules.rag.round_summarizer import summary_round
from app.modules.room_messages import broadcast_room_message
from app.repositories.room_message_repo import RoomMessageRepository
from app.shared.enums import RoomMessageRole, RoomMessageType

logger = logging.getLogger(__name__)

ROUND_SUMMARIZER_KEY = "round_summarizer"
MAX_ROUND_HISTORY = 10

RoundHistoryEntry = dict[str, str]


def append_round_summarizer_history(
    room: RoomModel,
    player_content: str,
    gm_content: str,
) -> tuple[list[RoundHistoryEntry], int]:
    history: list[RoundHistoryEntry] = room.agent_history.get(ROUND_SUMMARIZER_KEY, [])
    if not isinstance(history, list):
        history = []

    history.append({"role": "pl", "content": player_content})
    history.append({"role": "gm", "content": gm_content})

    if len(history) > MAX_ROUND_HISTORY:
        history = history[-MAX_ROUND_HISTORY:]

    room.agent_history[ROUND_SUMMARIZER_KEY] = history
    attributes.flag_modified(room, "agent_history")
    return history, 2


def format_history_for_summary(history: list[RoundHistoryEntry]) -> str:
    lines: list[str] = []
    for entry in history:
        label = "Player" if entry["role"] == "pl" else "GM"
        lines.append(f"<{label}>{entry['content']}</{label}>")
    return "\n".join(lines)


def format_history_detail(history: list[RoundHistoryEntry]) -> str:
    lines: list[str] = []
    for index, entry in enumerate(history, start=1):
        role_label = "玩家" if entry["role"] == "pl" else "GM"
        lines.append(f"{index}. [{role_label}] {entry['content']}")
    return "\n".join(lines)


async def run_round_summarizer_debug(
    room_id: UUID,
    participant_ids: list[UUID],
    history: list[RoundHistoryEntry],
) -> None:
    try:
        result = await summary_round(format_history_for_summary(history))
    except Exception:
        logger.exception("round summarizer failed: room_id=%s", room_id)
        return

    if result.summaries is None:
        return

    added_count = len(result.summaries)

    try:
        # format summaries
        formatted_summaries = []
        for i, summary in enumerate(result.summaries, start=1):
            formatted_summaries.append(f"{i}. {summary}")
        formatted_detail = "\n".join(formatted_summaries)

        async with AsyncSession(async_engine, expire_on_commit=False) as session:
            repo = RoomMessageRepository(session)
            debug_msg = await repo.create(
                room_id=room_id,
                sender_id=None,
                role=RoomMessageRole.SYSTEM,
                type=RoomMessageType.DEBUG,
                content=f"已新增 {added_count} 筆歷史",
                detail=formatted_detail,
            )
            await session.commit()
            await broadcast_room_message(participant_ids, debug_msg)
    except Exception:
        logger.exception("round summarizer debug message failed: room_id=%s", room_id)
