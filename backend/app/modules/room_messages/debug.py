from uuid import UUID

from app.db.uow import AsyncUnitOfWork
from app.models import RoomMessageModel
from app.shared.enums import RoomMessageRole, RoomMessageType

from .broadcast import broadcast_room_message


async def send_debug_room_message(
    uow: AsyncUnitOfWork,
    room_id: UUID,
    summary: str,
    detail: str,
) -> RoomMessageModel:
    msg = await uow.room_message_repo.create(
        room_id=room_id,
        sender_id=None,
        role=RoomMessageRole.SYSTEM,
        type=RoomMessageType.DEBUG,
        content=summary,
        detail=detail,
    )
    participants = await uow.room_repo.list_participants_with_details(room_id)
    participant_ids = [p.user_id for p in participants]
    await broadcast_room_message(participant_ids, msg)
    return msg
