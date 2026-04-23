from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import (
    RoomDetailResponse,
    RoomParticipantResponse,
)


class RegenerateInviteService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, room_id: UUID, current_user_id: UUID) -> RoomDetailResponse:
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        if room.host_id != current_user_id:
            raise HTTPException(
                status_code=403, detail="Only the host can regenerate the invite code"
            )

        room = await self._uow.room_repo.regenerate_invite_code(room)

        participants = await self._uow.room_repo.list_participants(room_id)
        room_data = RoomDetailResponse(
            id=room.id,
            scenario_id=room.scenario_id,
            host_id=room.host_id,
            name=room.name,
            description=room.description,
            status=room.status,
            invite_code=room.invite_code,
            participants=[
                RoomParticipantResponse(
                    user_id=p.user_id,
                    role=p.role,
                    is_ready=p.is_ready,
                    joined_at=p.joined_at,
                )
                for p in participants
            ],
        )
        return room_data
