from uuid import UUID

from app.db.uow import UnitOfWorkDependency
from app.features.scenarios.schemas.requests import CreateScenarioRequest
from app.features.scenarios.schemas.responses import ScenarioResponse


class CreateScenarioService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(
        self, body: CreateScenarioRequest, creator_id: UUID
    ) -> ScenarioResponse:
        scenario = await self._uow.scenario_repo.create(
            name=body.name,
            description=body.description,
            system=body.system,
            creator_id=creator_id,
            min_players=body.min_players,
            max_players=body.max_players,
            min_hours=body.min_hours,
            max_hours=body.max_hours,
        )
        return ScenarioResponse.model_validate(scenario)
