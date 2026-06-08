from logging import getLogger
from uuid import UUID

from app.core.websocket.manager import get_ws_connection_manager
from app.models import RoomMessageModel

logger = getLogger(__name__)


def room_message_to_ws_payload(msg: RoomMessageModel) -> dict:
    return {
        "id": str(msg.id),
        "room_id": str(msg.room_id),
        "sender_id": str(msg.sender_id) if msg.sender_id else None,
        "role": msg.role,
        "type": msg.type,
        "content": msg.content,
        "detail": msg.detail,
        "created_at": msg.created_at.isoformat(),
        "updated_at": msg.updated_at.isoformat(),
    }


async def broadcast_room_message(
    user_ids: list[UUID], msg: RoomMessageModel
) -> None:
    manager = get_ws_connection_manager()
    payload = room_message_to_ws_payload(msg)
    logger.info(
        "broadcast_room_message: msg_id=%s type=%s role=%s recipients=%d",
        msg.id,
        msg.type,
        msg.role,
        len(user_ids),
    )
    for user_id in user_ids:
        conn_count = manager.user_connection_count(user_id)
        logger.info(
            "broadcast_room_message: user_id=%s ws_connections=%d payload_type=%s",
            user_id,
            conn_count,
            payload.get("type"),
        )
        if conn_count == 0:
            logger.warning(
                "broadcast_room_message: user_id=%s has no active WS connection",
                user_id,
            )
        await manager.send_to_user(
            user_id,
            message_type="rooms.create_message",
            payload=payload,
        )


async def broadcast_ai_thinking(
    user_ids: list[UUID], room_id: UUID, *, active: bool
) -> None:
    manager = get_ws_connection_manager()
    payload = {"room_id": str(room_id), "active": active}
    for user_id in user_ids:
        await manager.send_to_user(
            user_id,
            message_type="rooms.ai_thinking",
            payload=payload,
        )
