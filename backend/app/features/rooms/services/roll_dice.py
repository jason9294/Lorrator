import random
from logging import getLogger
from uuid import UUID

from fastapi import HTTPException
from fastapi.background import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from app.db.sql import async_engine
from app.db.uow import UnitOfWorkDependency
from app.models import RoomModel
from app.models.links.room_participant_link import RoomParticipantLink
from app.modules.rag.client import client
from app.modules.room_messages import broadcast_ai_thinking, broadcast_room_message
from app.repositories.room_message_repo import RoomMessageRepository
from app.shared.enums import RoomMessageRole, RoomMessageType, RoomStatus

from ..schemas.requests import RollDiceRequest, SkillCheckRequest
from ..schemas.responses import RoomMessageResponse
from ._round_summarizer import (
    append_round_summarizer_history,
    run_round_summarizer_debug,
)

logger = getLogger(__name__)


def _skill_check_result(roll: int, skill_value: int) -> str:
    if roll == 1 or roll <= max(1, skill_value // 5):
        return "大成功！"
    elif roll <= skill_value // 2:
        return "困難成功"
    elif roll <= skill_value:
        return "成功"
    elif (skill_value < 50 and roll >= 96) or roll >= 100:
        return "大失敗！"
    else:
        return "失敗"


class RollDiceService:
    def __init__(self, uow: UnitOfWorkDependency, bg_tasks: BackgroundTasks) -> None:
        self._uow = uow
        self._bg_tasks = bg_tasks

    async def _validate_and_load(
        self, room_id: UUID, user_id: UUID
    ) -> tuple[RoomModel, list[RoomParticipantLink], list[UUID]]:
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        if room.status != RoomStatus.RUNNING:
            raise HTTPException(status_code=409, detail="Session is not running")

        participants = await self._uow.room_repo.list_participants_with_details(room_id)
        participant_ids = [p.user_id for p in participants]
        if user_id not in participant_ids:
            raise HTTPException(
                status_code=403, detail="You are not a participant of this room"
            )
        return room, participants, participant_ids

    def _schedule_agent_reply(
        self,
        participant_ids: list[UUID],
        room_id: UUID,
        ai_response: str,
        round_history: list[dict[str, str]],
        added_count: int,
    ) -> None:
        async def _delayed_reply() -> None:
            logger.info(
                "_delayed_reply started: room_id=%s participants=%s response_len=%d",
                room_id,
                participant_ids,
                len(ai_response),
            )
            try:
                async with AsyncSession(
                    async_engine, expire_on_commit=False
                ) as session:
                    repo = RoomMessageRepository(session)
                    agent_msg = await repo.create(
                        room_id=room_id,
                        sender_id=None,
                        role=RoomMessageRole.AGENT,
                        content=ai_response,
                    )
                    logger.info(
                        "created agent_msg: id=%s type=%s",
                        agent_msg.id,
                        agent_msg.type,
                    )
                    await session.commit()
                    logger.info("committed agent_msg=%s", agent_msg.id)
                    await broadcast_room_message(participant_ids, agent_msg)
                    logger.info("broadcast agent_msg done: id=%s", agent_msg.id)
                await run_round_summarizer_debug(
                    room_id, participant_ids, round_history
                )
            except Exception:
                logger.exception("_delayed_reply failed: room_id=%s", room_id)
                raise
            finally:
                logger.info(
                    "_delayed_reply finally: clearing ai_thinking room_id=%s", room_id
                )
                await broadcast_ai_thinking(participant_ids, room_id, active=False)

        logger.info(
            "scheduling _delayed_reply: room_id=%s participants=%s",
            room_id,
            participant_ids,
        )
        self._bg_tasks.add_task(_delayed_reply)

    async def _run_agent_turn(
        self,
        room: RoomModel,
        participant_ids: list[UUID],
        room_id: UUID,
        user_prompt: str,
        player_content: str,
    ) -> None:
        room.agent_history["kp"].append({"role": "user", "content": user_prompt})
        logger.info("_run_agent_turn: calling AI room_id=%s", room_id)

        try:
            response = await client.responses.create(
                model="gpt-5.4",
                input=room.agent_history["kp"],
            )
        except Exception:
            logger.exception("_run_agent_turn: AI call failed room_id=%s", room_id)
            await broadcast_ai_thinking(participant_ids, room_id, active=False)
            raise

        logger.info(
            "_run_agent_turn: AI response received room_id=%s len=%d",
            room_id,
            len(response.output_text),
        )
        room.agent_history["kp"].append(
            {"role": "assistant", "content": response.output_text}
        )

        round_history, added_count = append_round_summarizer_history(
            room, player_content, response.output_text
        )

        attributes.flag_modified(room, "agent_history")
        await self._uow.room_repo.save(room)
        self._schedule_agent_reply(
            participant_ids,
            room_id,
            response.output_text,
            round_history,
            added_count,
        )

    async def roll(
        self, room_id: UUID, body: RollDiceRequest, sender_id: UUID
    ) -> RoomMessageResponse:
        room, participants, participant_ids = await self._validate_and_load(
            room_id, sender_id
        )

        results = [random.randint(1, body.faces) for _ in range(body.count)]
        total = sum(results)
        results_str = ", ".join(str(r) for r in results)
        content = f"🎲 擲出了 {body.count}d{body.faces}：[{results_str}] = {total}"

        msg = await self._uow.room_message_repo.create(
            room_id=room_id,
            sender_id=sender_id,
            role=RoomMessageRole.SYSTEM,
            type=RoomMessageType.DICE,
            content=content,
        )
        await broadcast_room_message(participant_ids, msg)
        await broadcast_ai_thinking(participant_ids, room_id, active=True)

        current_participant: RoomParticipantLink = next(  # type: ignore
            (p for p in participants if p.user_id == sender_id), None
        )

        user_prompt = f'<Character name="{current_participant.character.name}"><dice>{content}</dice></Character>'
        await self._run_agent_turn(
            room, participant_ids, room_id, user_prompt, player_content=content
        )
        return RoomMessageResponse.model_validate(msg)

    async def skill_check(
        self, room_id: UUID, body: SkillCheckRequest, sender_id: UUID
    ) -> RoomMessageResponse:
        room, participants, participant_ids = await self._validate_and_load(
            room_id, sender_id
        )

        roll = random.randint(1, 100)
        result_text = _skill_check_result(roll, body.skill_value)
        content = (
            f"🎲 進行【{body.skill_name} {body.skill_value}%】技能檢定："
            f"擲出 {roll} → {result_text}"
        )

        msg = await self._uow.room_message_repo.create(
            room_id=room_id,
            sender_id=sender_id,
            role=RoomMessageRole.SYSTEM,
            type=RoomMessageType.DICE,
            content=content,
        )
        await broadcast_room_message(participant_ids, msg)
        await broadcast_ai_thinking(participant_ids, room_id, active=True)

        current_participant: RoomParticipantLink = next(  # type: ignore
            (p for p in participants if p.user_id == sender_id), None
        )

        user_prompt = f'<Character name="{current_participant.character.name}"><dice>{content}</dice></Character>'
        await self._run_agent_turn(
            room, participant_ids, room_id, user_prompt, player_content=content
        )
        return RoomMessageResponse.model_validate(msg)
