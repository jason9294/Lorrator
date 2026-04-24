from uuid import UUID

from fastapi import HTTPException

from app.core.websocket.manager import get_ws_connection_manager
from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.requests import JoinRoomRequest
from app.features.rooms.schemas.responses import RoomDetailResponse
from app.shared.enums import RoomStatus

from ._helpers import build_room_detail


class JoinRoomService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(
        self, body: JoinRoomRequest, current_user_id: UUID
    ) -> RoomDetailResponse:
        # validate invite code
        room = await self._uow.room_repo.get_by_invite_code(body.invite_code)
        if room is None:
            raise HTTPException(status_code=404, detail="Invalid invite code")

        # validate room status
        if room.status != RoomStatus.PREPARING:
            raise HTTPException(
                status_code=409,
                detail="This room is no longer accepting new participants",
            )

        current_user = await self._uow.user_repo.get_by_id(current_user_id)
        if current_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        participants = await self._uow.room_repo.list_participants(room.id)
        if current_user_id in [p.user_id for p in participants]:
            raise HTTPException(status_code=409, detail="You are already in this room")

        current_participant = await self._uow.room_repo.add_participant(
            room_id=room.id, user_id=current_user_id, role="player"
        )

        ws_manager = get_ws_connection_manager()
        for participant in participants:
            await ws_manager.send_to_user(
                participant.user_id,
                message_type="rooms.join_room",
                payload={
                    "room_id": str(room.id),
                    "user_id": str(current_user.id),
                    "role": "PLAYER",
                    "is_ready": current_participant.is_ready,
                    "joined_at": current_participant.joined_at.isoformat(),
                },
            )

        return await build_room_detail(self._uow, room)
