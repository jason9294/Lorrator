import asyncio
from uuid import UUID

from fastapi import HTTPException

from app.core.websocket.manager import get_ws_connection_manager
from app.db.uow import UnitOfWorkDependency
from app.models import RoomMessageModel
from app.shared.enums import RoomMessageRole

from ..schemas.requests import SendMessageRequest
from ..schemas.responses import RoomMessageResponse


class SendRoomMessageService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow
        self._manager = get_ws_connection_manager()

    async def _broadcast_message(
        self, user_ids: list[UUID], msg: RoomMessageModel
    ) -> None:
        for user_id in user_ids:
            await self._manager.send_to_user(
                user_id,
                message_type="rooms.create_message",
                payload={
                    "room_id": str(msg.room_id),
                    "sender_id": str(msg.sender_id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "updated_at": msg.updated_at.isoformat(),
                },
            )

    async def execute(
        self,
        room_id: UUID,
        body: SendMessageRequest,
        sender_id: UUID,
    ) -> RoomMessageResponse:
        # validate room exists
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        # validate sender is a participant of the room
        participants = await self._uow.room_repo.list_participants(room_id)
        participant_ids = [p.user_id for p in participants]
        if sender_id not in participant_ids:
            raise HTTPException(
                status_code=403, detail="You are not a participant of this room"
            )

        # create player message
        msg = await self._uow.room_message_repo.create(
            room_id=room_id,
            sender_id=sender_id,
            role=RoomMessageRole.PLAYER,
            content=body.content,
        )
        await self._broadcast_message(participant_ids, msg)

        # TODO 測試用：HTTP 收到訊息後，延遲一段時間再透過 WebSocket 回推給發送者
        async def _delayed_ws_reply() -> None:
            await asyncio.sleep(1.2)

            # create agent message
            await self._uow.room_message_repo.create(
                room_id=room_id,
                sender_id=None,
                role=RoomMessageRole.AGENT,
                content=f'這是一則測試訊息: 你說"{body.content}"',
            )

            # send message to all participants
            await self._broadcast_message(
                participant_ids,
                msg,
            )

        asyncio.create_task(_delayed_ws_reply())
        return RoomMessageResponse.model_validate(msg)
