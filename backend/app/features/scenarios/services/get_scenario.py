from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.scenarios.schemas.responses import ScenarioResponse
from app.shared.enums import ScenarioStatus


class GetScenarioService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, scenario_id: UUID, current_user_id: UUID) -> ScenarioResponse:
        scenario = await self._uow.scenario_repo.get_by_id(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")

        if scenario.status == ScenarioStatus.DRAFT and scenario.creator_id != current_user_id:
            raise HTTPException(status_code=403, detail="This scenario is a draft and only visible to its creator")

        return ScenarioResponse.model_validate(scenario)
