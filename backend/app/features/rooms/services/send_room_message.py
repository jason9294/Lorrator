from uuid import UUID

from fastapi import HTTPException

from app.core.websocket.manager import get_ws_connection_manager
from app.db.uow import UnitOfWorkDependency

from ..schemas.requests import SendMessageRequest
from ..schemas.responses import RoomMessageResponse


class SendRoomMessageService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(
        self,
        room_id: UUID,
        body: SendMessageRequest,
        sender_id: UUID,
    ) -> RoomMessageResponse:
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")
        msg = await self._uow.room_message_repo.create(
            room_id=room_id,
            sender_id=sender_id,
            content=body.content,
        )

        # TODO 測試用：HTTP 收到訊息後，延遲一段時間再透過 WebSocket 回推給發送者
        async def _delayed_ws_reply() -> None:
            import asyncio

            await asyncio.sleep(1.2)
            manager = get_ws_connection_manager()
            await manager.send_to_user(
                sender_id,
                message_type="rooms.test_message",
                payload={
                    "room_id": str(room_id),
                    "content": f'這是一則測試訊息: 你說"{body.content}"',
                },
            )

        import asyncio

        asyncio.create_task(_delayed_ws_reply())
        return RoomMessageResponse.model_validate(msg)
