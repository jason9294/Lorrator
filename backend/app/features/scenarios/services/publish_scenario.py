from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.scenarios.schemas.responses import ScenarioResponse
from app.shared.enums import DocumentStatus, ScenarioStatus


class PublishScenarioService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, scenario_id: UUID, current_user_id: UUID) -> ScenarioResponse:
        scenario = await self._uow.scenario_repo.get_by_id(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")

        if scenario.creator_id != current_user_id:
            raise HTTPException(status_code=403, detail="Only the creator can publish this scenario")

        if scenario.status == ScenarioStatus.PUBLISHED:
            raise HTTPException(status_code=409, detail="Scenario is already published")

        documents = await self._uow.document_repo.list_by_scenario(scenario_id)
        if not documents:
            raise HTTPException(
                status_code=422,
                detail="Scenario must have at least one document before publishing",
            )

        non_completed = [d for d in documents if d.status != DocumentStatus.COMPLETED]
        if non_completed:
            raise HTTPException(
                status_code=422,
                detail="All documents must be processed (COMPLETED) before publishing",
            )

        scenario = await self._uow.scenario_repo.publish(scenario)
        return ScenarioResponse.model_validate(scenario)
