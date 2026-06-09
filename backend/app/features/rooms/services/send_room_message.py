from uuid import UUID

from fastapi import HTTPException
from fastapi.background import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from app.db.sql import async_engine
from app.db.uow import UnitOfWorkDependency
from app.models import RoomParticipantLink
from app.modules.rag.client import client
from app.helpers.room_message_broadcast import (
    broadcast_ai_thinking,
    broadcast_room_message,
)
from app.repositories.room_message_repo import RoomMessageRepository
from app.shared.enums import RoomMessageRole, RoomMessageType

# API Schema
from ..schemas.requests import SendMessageRequest
from ..schemas.responses import RoomMessageResponse
from ._round_summarizer import (
    append_round_summarizer_history,
    run_round_summarizer_debug,
)


class SendRoomMessageService:
    def __init__(self, uow: UnitOfWorkDependency, bg_tasks: BackgroundTasks) -> None:
        self._uow = uow
        self._bg_tasks = bg_tasks

    async def execute(
        self,
        room_id: UUID,
        body: SendMessageRequest,
        sender_id: UUID,
    ) -> RoomMessageResponse:
        room = await self._uow.room_repo.get_by_id(room_id)

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

        # broadcast player message to all participants
        await broadcast_room_message(msg)

        # 通知所有人 AI 思考中，鎖住輸入框
        await broadcast_ai_thinking(room_id, active=True)

        current_participant: RoomParticipantLink = next(  # type: ignore
            (p for p in participants if p.user_id == sender_id), None
        )

        user_prompt = f'<Character name="{current_participant.character.name}"><role_play>{body.content}</role_play></Character>'
        room.agent_history["kp"].append({"role": "user", "content": user_prompt})

        try:
            response = await client.responses.create(
                model="gpt-5.4",
                input=room.agent_history["kp"],
            )
        except Exception:
            await broadcast_ai_thinking(room_id, active=False)
            raise

        room.agent_history["kp"].append(
            {"role": "assistant", "content": response.output_text}
        )

        round_history, _ = append_round_summarizer_history(
            room, body.content, response.output_text
        )

        attributes.flag_modified(room, "agent_history")
        await self._uow.room_repo.save(room)

        async def _delayed_ws_reply() -> None:
            try:
                async with AsyncSession(
                    async_engine, expire_on_commit=False
                ) as session:
                    repo = RoomMessageRepository(session)
                    agent_msg = await repo.create(
                        room_id=room_id,
                        sender_id=None,
                        role=RoomMessageRole.AGENT,
                        content=response.output_text,
                    )
                    await session.commit()

                    await broadcast_room_message(agent_msg)
                await run_round_summarizer_debug(
                    room_id, participant_ids, round_history
                )
            finally:
                await broadcast_ai_thinking(room_id, active=False)

        self._bg_tasks.add_task(_delayed_ws_reply)
        return RoomMessageResponse.model_validate(msg)
