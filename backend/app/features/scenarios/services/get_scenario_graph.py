from uuid import UUID

from fastapi import HTTPException, status
from neo4j.graph import Node, Relationship

from app.db.graph import neo4j_driver
from app.db.uow import UnitOfWorkDependency


class GetScenarioGraphService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, scenario_id: UUID) -> None:
        # validate scenario exists
        scenario = await self._uow.scenario_repo.get_by_id(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # get graph
        async with neo4j_driver.session() as session:
            query = """
                MATCH (a:Entity {group_id: $group_id})
                OPTIONAL MATCH (a)-[r]-(b:Entity {group_id: $group_id})
                RETURN a, r, b
            """
            result = await session.run(
                query,
                group_id=scenario.graph_group_id,
            )

            async for record in result:
                a: Node | None = record["a"]
                r: Relationship | None = record["r"]
                b: Node | None = record["b"]

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Knowledge graph not implemented",
        )
