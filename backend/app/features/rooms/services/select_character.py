from uuid import UUID

from fastapi import HTTPException

from app.core.realtime import get_ws_connection_manager
from app.core.realtime.websocket.envelopes import RoomsSelectCharacterEnvelope
from app.core.realtime.websocket.topics import WsTopic
from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.requests import SelectCharacterRequest
from app.features.rooms.schemas.responses import RoomDetailResponse
from app.shared.enums import RoomStatus

from ._helpers import build_room_detail


class SelectCharacterService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow
        self._ws_manager = get_ws_connection_manager()

    async def execute(
        self,
        room_id: UUID,
        body: SelectCharacterRequest,
        current_user_id: UUID,
    ) -> RoomDetailResponse:
        room = await self._uow.room_repo.find_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        if room.status != RoomStatus.PREPARING:
            raise HTTPException(
                status_code=409, detail="Room is not in preparing stage"
            )

        participants = await self._uow.room_repo.list_participants(room_id)
        participant = next(
            (p for p in participants if p.user_id == current_user_id), None
        )
        if participant is None:
            raise HTTPException(
                status_code=403, detail="You are not a participant of this room"
            )

        if participant.is_ready:
            raise HTTPException(
                status_code=409,
                detail="Cannot change character while ready; cancel ready first",
            )

        if body.character_id is not None:
            character = await self._uow.character_repo.get_by_id(body.character_id)
            if character is None or character.owner_id != current_user_id:
                raise HTTPException(status_code=404, detail="Character not found")

        await self._uow.room_repo.set_participant_character(
            room_id, current_user_id, body.character_id
        )

        character_name: str | None = None
        if body.character_id is not None:
            character = await self._uow.character_repo.get_by_id(body.character_id)
            character_name = character.name if character else None

        await self._ws_manager.send_to_topic(
            WsTopic.room(room_id),
            RoomsSelectCharacterEnvelope(
                room_id=str(room_id),
                user_id=str(current_user_id),
                character_id=str(body.character_id) if body.character_id else None,
                character_name=character_name,
            ),
        )

        return await build_room_detail(self._uow, room)
