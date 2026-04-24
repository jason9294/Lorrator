from uuid import UUID

from fastapi import HTTPException

from app.core.websocket.manager import get_ws_connection_manager
from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import RoomDetailResponse

from ._helpers import build_room_detail


class KickParticipantService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow
        self._ws_manager = get_ws_connection_manager()

    async def execute(
        self, room_id: UUID, target_user_id: UUID, current_user_id: UUID
    ) -> RoomDetailResponse:
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        if room.host_id != current_user_id:
            raise HTTPException(
                status_code=403, detail="Only the host can kick participants"
            )

        if target_user_id == current_user_id:
            raise HTTPException(status_code=400, detail="Host cannot kick themselves")

        participant = await self._uow.room_repo.get_participant(room_id, target_user_id)
        if participant is None:
            raise HTTPException(status_code=404, detail="Participant not found")

        existing_participants = await self._uow.room_repo.list_participants(room_id)
        existing_participant_ids = [p.user_id for p in existing_participants]

        await self._uow.room_repo.remove_participant(participant)

        # broadcast kick event (include kicked user)
        for user_id in set([*existing_participant_ids, target_user_id]):
            try:
                await self._ws_manager.send_to_user(
                    user_id,
                    message_type="rooms.kick",
                    payload={
                        "room_id": str(room_id),
                        "user_id": str(target_user_id),
                    },
                )
            finally:
                pass

        return await build_room_detail(self._uow, room)
