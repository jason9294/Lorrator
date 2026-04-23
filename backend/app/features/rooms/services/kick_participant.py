from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import RoomDetailResponse, RoomParticipantResponse


class KickParticipantService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(
        self, room_id: UUID, target_user_id: UUID, current_user_id: UUID
    ) -> RoomDetailResponse:
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        if room.host_id != current_user_id:
            raise HTTPException(status_code=403, detail="Only the host can kick participants")

        if target_user_id == current_user_id:
            raise HTTPException(status_code=400, detail="Host cannot kick themselves")

        participant = await self._uow.room_repo.get_participant(room_id, target_user_id)
        if participant is None:
            raise HTTPException(status_code=404, detail="Participant not found")

        await self._uow.room_repo.remove_participant(participant)

        participants = await self._uow.room_repo.list_participants(room_id)
        room_data = RoomDetailResponse.model_validate(room)
        room_data.participants = [RoomParticipantResponse.model_validate(p) for p in participants]
        return room_data
