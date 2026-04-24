from uuid import UUID

from fastapi import HTTPException
from fastapi.background import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from app.core.websocket.manager import get_ws_connection_manager
from app.db.sql import async_engine
from app.db.uow import UnitOfWorkDependency
from app.models import RoomMessageModel, RoomParticipantLink
from app.modules.rag.client import client
from app.repositories.room_message_repo import RoomMessageRepository
from app.shared.enums import RoomMessageRole, RoomMessageType

from ..schemas.requests import SendMessageRequest
from ..schemas.responses import RoomMessageResponse


class SendRoomMessageService:
    def __init__(self, uow: UnitOfWorkDependency, bg_tasks: BackgroundTasks) -> None:
        self._uow = uow
        self._manager = get_ws_connection_manager()
        self._bg_tasks = bg_tasks

    async def _broadcast_message(
        self, user_ids: list[UUID], msg: RoomMessageModel
    ) -> None:
        for user_id in user_ids:
            await self._manager.send_to_user(
                user_id,
                message_type="rooms.create_message",
                payload={
                    "id": str(msg.id),
                    "room_id": str(msg.room_id),
                    "sender_id": str(msg.sender_id) if msg.sender_id else None,
                    "role": msg.role,
                    "type": msg.type,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "updated_at": msg.updated_at.isoformat(),
                },
            )

    async def _broadcast_ai_thinking(self, user_ids: list[UUID], room_id: UUID) -> None:
        for user_id in user_ids:
            await self._manager.send_to_user(
                user_id,
                message_type="rooms.ai_thinking",
                payload={"room_id": str(room_id)},
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
        participants = await self._uow.room_repo.list_participants_with_details(room_id)
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
            type=RoomMessageType.CHAT,
            content=body.content,
        )
        await self._broadcast_message(participant_ids, msg)

        # 通知所有人 AI 思考中，鎖住輸入框
        await self._broadcast_ai_thinking(participant_ids, room_id)

        current_participant: RoomParticipantLink = next(  # type: ignore
            (p for p in participants if p.user_id == sender_id), None
        )

        user_prompt = f'<Character name="{current_participant.character.name}"><role_play>{body.content}</role_play></Character>'
        room.agent_history["kp"].append({"role": "user", "content": user_prompt})

        response = await client.responses.create(
            model="gpt-5.4",
            input=room.agent_history["kp"],
        )

        room.agent_history["kp"].append(
            {"role": "assistant", "content": response.output_text}
        )

        attributes.flag_modified(room, "agent_history")
        await self._uow.room_repo.save(room)

        async def _delayed_ws_reply() -> None:
            async with AsyncSession(async_engine, expire_on_commit=False) as session:
                repo = RoomMessageRepository(session)
                agent_msg = await repo.create(
                    room_id=room_id,
                    sender_id=None,
                    role=RoomMessageRole.AGENT,
                    content=response.output_text,
                )
                await session.commit()

                await self._broadcast_message(participant_ids, agent_msg)

        self._bg_tasks.add_task(_delayed_ws_reply)
        return RoomMessageResponse.model_validate(msg)
