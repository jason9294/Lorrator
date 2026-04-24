from uuid import UUID

from fastapi import HTTPException

from app.core.websocket.manager import get_ws_connection_manager
from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import RoomDetailResponse
from app.shared.enums import RoomStatus

from ._helpers import build_room_detail


class SetReadyService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow
        self._ws_manager = get_ws_connection_manager()

    async def execute(
        self, room_id: UUID, is_ready: bool, current_user_id: UUID
    ) -> RoomDetailResponse:
        # validate room id
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        # validate room status
        if room.status != RoomStatus.PREPARING:
            raise HTTPException(
                status_code=409, detail="Room is not in preparing stage"
            )

        # validate participant
        participants = await self._uow.room_repo.list_participants(room_id)
        participant_ids = [p.user_id for p in participants]
        if current_user_id not in participant_ids:
            raise HTTPException(
                status_code=403, detail="You are not a participant of this room"
            )

        # set ready status
        await self._uow.room_repo.set_participant_ready(
            room_id, current_user_id, is_ready
        )

        # broadcast ready status
        for user_id in participant_ids:
            try:
                await self._ws_manager.send_to_user(
                    user_id,
                    message_type="rooms.set_ready",
                    payload={
                        "room_id": str(room_id),
                        "user_id": str(current_user_id),
                        "is_ready": is_ready,
                    },
                )
            finally:
                pass

        return await build_room_detail(self._uow, room)
