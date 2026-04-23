from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import RoomMessageResponse
from app.shared.enums import RoomStatus


class ListRoomMessagesService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, room_id: UUID, current_user_id: UUID) -> list[RoomMessageResponse]:
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        participant = await self._uow.room_repo.get_participant(room_id, current_user_id)
        if participant is None:
            raise HTTPException(status_code=403, detail="You are not a participant of this room")

        if room.status != RoomStatus.RUNNING:
            raise HTTPException(status_code=409, detail="Session has not started yet")

        messages = await self._uow.room_message_repo.list_by_room(room_id)
        return [RoomMessageResponse.model_validate(m) for m in messages]
