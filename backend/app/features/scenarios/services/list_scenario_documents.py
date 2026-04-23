from uuid import UUID

from fastapi import HTTPException

from app.db.uow import UnitOfWorkDependency
from app.features.scenarios.schemas.responses import DocumentResponse


class ListScenarioDocumentsService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, scenario_id: UUID) -> list[DocumentResponse]:
        scenario = await self._uow.scenario_repo.get_by_id(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")
        docs = await self._uow.document_repo.list_by_scenario(scenario_id)
        return [DocumentResponse.model_validate(d) for d in docs]
