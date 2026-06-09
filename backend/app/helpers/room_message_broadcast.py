from logging import getLogger
from uuid import UUID

from app.core.realtime.websocket.envelopes import (
    RoomsAiThinkingEnvelope,
    RoomsCreateMessageEnvelope,
)
from app.core.realtime.websocket.manager import get_ws_connection_manager
from app.core.realtime.websocket.topics import WsTopic
from app.models import RoomMessageModel

logger = getLogger(__name__)


async def broadcast_room_message(msg: RoomMessageModel) -> None:
    topic = WsTopic.room(msg.room_id)
    envelope = RoomsCreateMessageEnvelope.from_model(msg)
    logger.info(
        "broadcast_room_message: msg_id=%s type=%s role=%s topic=%s",
        msg.id,
        msg.type,
        msg.role,
        topic,
    )
    await get_ws_connection_manager().send_to_topic(topic, envelope)


async def broadcast_ai_thinking(room_id: UUID, *, active: bool) -> None:
    topic = WsTopic.room(room_id)
    envelope = RoomsAiThinkingEnvelope.for_room(room_id, active=active)
    await get_ws_connection_manager().send_to_topic(topic, envelope)
