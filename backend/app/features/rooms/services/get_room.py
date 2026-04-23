from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import RoomDetailResponse, RoomParticipantResponse


class GetRoomService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, room_id: UUID, current_user_id: UUID) -> RoomDetailResponse:
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        participant = await self._uow.room_repo.get_participant(room_id, current_user_id)
        if participant is None:
            raise HTTPException(status_code=403, detail="You are not a participant of this room")

        participants = await self._uow.room_repo.list_participants(room_id)
        room_data = RoomDetailResponse.model_validate(room)
        room_data.participants = [RoomParticipantResponse.model_validate(p) for p in participants]
        return room_data
