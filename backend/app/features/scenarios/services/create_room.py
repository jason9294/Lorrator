from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.scenarios.schemas.requests import CreateRoomRequest
from app.features.scenarios.schemas.responses import RoomDetailResponse, RoomParticipantResponse
from app.shared.enums import ScenarioStatus


class CreateRoomService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(
        self,
        scenario_id: UUID,
        body: CreateRoomRequest,
        host_id: UUID,
    ) -> RoomDetailResponse:
        scenario = await self._uow.scenario_repo.get_by_id(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")

        if scenario.status != ScenarioStatus.PUBLISHED:
            raise HTTPException(
                status_code=409,
                detail="Only published scenarios can have rooms created for them",
            )

        room = await self._uow.room_repo.create(
            scenario_id=scenario_id,
            host_id=host_id,
            name=body.name,
            description=body.description,
        )
        participant = await self._uow.room_repo.add_participant(
            room_id=room.id, user_id=host_id, role="gm"
        )

        room_data = RoomDetailResponse.model_validate(room)
        room_data.participants = [RoomParticipantResponse.model_validate(participant)]
        return room_data
