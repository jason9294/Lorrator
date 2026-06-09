from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import RoomDetailResponse

from ._helpers import build_room_detail


class GetRoomService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, room_id: UUID, current_user_id: UUID) -> RoomDetailResponse:
        room = await self._uow.room_repo.find_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        participant = await self._uow.room_repo.get_participant(
            room_id, current_user_id
        )
        if participant is None:
            raise HTTPException(
                status_code=403, detail="You are not a participant of this room"
            )

        return await build_room_detail(self._uow, room)
