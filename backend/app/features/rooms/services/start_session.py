from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import RoomDetailResponse, RoomParticipantResponse
from app.shared.enums import RoomStatus


class StartSessionService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, room_id: UUID, current_user_id: UUID) -> RoomDetailResponse:
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        if room.host_id != current_user_id:
            raise HTTPException(status_code=403, detail="Only the host can start the session")

        if room.status != RoomStatus.PREPARING:
            raise HTTPException(status_code=409, detail="Room is not in preparing stage")

        participants = await self._uow.room_repo.list_participants(room_id)

        if len(participants) < 1:
            raise HTTPException(status_code=409, detail="Room must have at least one participant")

        not_ready = [p for p in participants if not p.is_ready]
        if not_ready:
            raise HTTPException(
                status_code=409,
                detail=f"{len(not_ready)} participant(s) are not ready yet",
            )

        room = await self._uow.room_repo.update_status(room, RoomStatus.RUNNING)

        room_data = RoomDetailResponse.model_validate(room)
        room_data.participants = [RoomParticipantResponse.model_validate(p) for p in participants]
        return room_data
