from uuid import UUID

from app.db.uow import UnitOfWorkDependency
from app.features.scenarios.schemas.responses import ScenarioResponse


class ListScenariosService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, current_user_id: UUID) -> list[ScenarioResponse]:
        scenarios = await self._uow.scenario_repo.list_visible_to_user(current_user_id)
        return [ScenarioResponse.model_validate(s) for s in scenarios]
