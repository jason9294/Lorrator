import os
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import attributes

from app.core import get_settings
from app.db.uow import UnitOfWorkDependency
from app.features.rooms.schemas.responses import RoomDetailResponse
from app.modules.rag.client import client
from app.modules.rag.prompts.kp import PROMPTS
from app.shared.enums import RoomMessageRole, RoomMessageType, RoomStatus

from ._helpers import build_room_detail


class StartSessionService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, room_id: UUID, current_user_id: UUID) -> RoomDetailResponse:
        room = await self._uow.room_repo.get_by_id(room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        if room.host_id != current_user_id:
            raise HTTPException(
                status_code=403, detail="Only the host can start the session"
            )

        if room.status != RoomStatus.PREPARING:
            raise HTTPException(
                status_code=409, detail="Room is not in preparing stage"
            )

        participants = await self._uow.room_repo.list_participants_with_details(room_id)

        if len(participants) < 1:
            raise HTTPException(
                status_code=409, detail="Room must have at least one participant"
            )

        not_ready = [p for p in participants if not p.is_ready]
        if not_ready:
            raise HTTPException(
                status_code=409,
                detail=f"{len(not_ready)} participant(s) are not ready yet",
            )

        room = await self._uow.room_repo.update_status(room, RoomStatus.RUNNING)

        # get document
        scenario = await self._uow.scenario_repo.get_by_id(room.scenario_id)
        scenario_docs = await self._uow.document_repo.list_by_scenario(scenario.id)  # type: ignore
        first_doc = scenario_docs[0]

        # get markdown content of the first document
        uploads_dir = get_settings().UPLOAD_DIR
        path = os.path.join(uploads_dir, first_doc.md_path)
        with open(path, "r", encoding="utf-8") as f:
            scenario_content = f.read()

        # get player and character to json string
        player = []
        character = []
        for i, p in enumerate(participants):
            player.append(
                {
                    "id": f"player_{i}",
                    "name": p.user.nickname if p.user.nickname else p.user.username,
                }
            )
            character.append(
                {
                    "id": f"character_{i}",
                    "owner_id": f"player_{i}",
                    "name": p.character.name,
                }
            )

        # let the agent start the session
        sys_prompt = PROMPTS["trpg_kp_system_prompt"].format(
            output_language="繁體中文",
            scenario=scenario_content,
            player=...,
            character=...,
        )

        agent_history = room.agent_history
        agent_history["kp"] = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": "Now start the session."},
        ]

        response = await client.responses.create(
            model="gpt-5.4",
            input=agent_history["kp"],
        )

        agent_history["kp"].append(
            {"role": "assistant", "content": response.output_text}
        )

        # save agent history to database
        # flag_modified is required because agent_history is a JSONB column;
        # SQLAlchemy won't detect in-place dict mutations without it.
        room.agent_history = agent_history
        attributes.flag_modified(room, "agent_history")
        await self._uow.room_repo.save(room)

        await self._uow.room_message_repo.create(
            room_id=room_id,
            sender_id=None,
            content=response.output_text,
            role=RoomMessageRole.AGENT,
            type=RoomMessageType.CHAT,
        )

        return await build_room_detail(self._uow, room)
