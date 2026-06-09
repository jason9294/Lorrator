from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import RoomDetailResponse

from ._helpers import build_room_detail


class RegenerateInviteService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, room_id: UUID, current_user_id: UUID) -> RoomDetailResponse:
        room = await self._uow.room_repo.find_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        if room.host_id != current_user_id:
            raise HTTPException(
                status_code=403, detail="Only the host can regenerate the invite code"
            )

        room = await self._uow.room_repo.regenerate_invite_code(room)

        return await build_room_detail(self._uow, room)
