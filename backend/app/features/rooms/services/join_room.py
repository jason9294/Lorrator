from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.requests import JoinRoomRequest
from app.features.rooms.schemas.responses import RoomDetailResponse, RoomParticipantResponse
from app.shared.enums import RoomStatus


class JoinRoomService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, body: JoinRoomRequest, current_user_id: UUID) -> RoomDetailResponse:
        room = await self._uow.room_repo.get_by_invite_code(body.invite_code)
        if room is None:
            raise HTTPException(status_code=404, detail="Invalid invite code")

        if room.status != RoomStatus.PREPARING:
            raise HTTPException(status_code=409, detail="This room is no longer accepting new participants")

        existing = await self._uow.room_repo.get_participant(room.id, current_user_id)
        if existing is not None:
            raise HTTPException(status_code=409, detail="You are already in this room")

        await self._uow.room_repo.add_participant(
            room_id=room.id, user_id=current_user_id, role="player"
        )

        participants = await self._uow.room_repo.list_participants(room.id)
        room_data = RoomDetailResponse.model_validate(room)
        room_data.participants = [RoomParticipantResponse.model_validate(p) for p in participants]
        return room_data
