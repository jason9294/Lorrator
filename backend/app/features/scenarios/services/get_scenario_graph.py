from uuid import UUID

from fastapi import HTTPException
from neo4j.graph import Node, Relationship

from app.db.graph import neo4j_driver
from app.db.uow import UnitOfWorkDependency
from app.repositories.graph_repo import GraphRepo

from ..schemas.responses import (
    ScenarioGraphEdgeResponse,
    ScenarioGraphNodeResponse,
    ScenarioGraphResponse,
)


class GetScenarioGraphService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, scenario_id: UUID) -> ScenarioGraphResponse:
        # validate scenario exists
        scenario = await self._uow.scenario_repo.get_by_id(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found")

        nodes_by_id: dict[str, ScenarioGraphNodeResponse] = {}
        edges_by_id: dict[str, ScenarioGraphEdgeResponse] = {}

        def _node_id(n: Node) -> str:
            # element_id is stable-ish across drivers and unique within DB
            return getattr(n, "element_id", None) or str(getattr(n, "id", ""))

        def _node_type(n: Node) -> str:
            labels = list(getattr(n, "labels", []) or [])
            for lb in labels:
                if lb != "Entity":
                    return str(lb)
            props = dict(n)
            t = props.get("type") or props.get("entity_type")
            return str(t) if t else "Entity"

        def _node_label(n: Node) -> str:
            props = dict(n)
            for k in ("name", "label", "title"):
                v = props.get(k)
                if isinstance(v, str) and v.strip():
                    return v
            return _node_id(n)

        def _node_description(n: Node) -> str:
            props = dict(n)
            v = props.get("description")
            return v if isinstance(v, str) else ""

        # get graph
        async with neo4j_driver.session() as session:
            repo = GraphRepo(session)
            result = await repo.query_scenario_graph(str(scenario.graph_group_id))

            async for record in result:
                n: Node | None = record["n"]
                r: Relationship | None = record["r"]
                m: Node | None = record["m"]
                if n is not None:
                    aid = _node_id(n)
                    if aid not in nodes_by_id:
                        nodes_by_id[aid] = ScenarioGraphNodeResponse(
                            id=aid,
                            type=_node_type(n),
                            label=_node_label(n),
                            description=_node_description(n),
                        )
                if m is not None:
                    bid = _node_id(m)
                    if bid not in nodes_by_id:
                        nodes_by_id[bid] = ScenarioGraphNodeResponse(
                            id=bid,
                            type=_node_type(m),
                            label=_node_label(m),
                            description=_node_description(m),
                        )
                if n is not None and m is not None and r is not None:
                    rid = getattr(r, "element_id", None) or str(getattr(r, "id", ""))
                    if rid and rid not in edges_by_id:
                        edges_by_id[rid] = ScenarioGraphEdgeResponse(
                            id=rid,
                            source=_node_id(n),
                            target=_node_id(m),
                            type=str(getattr(r, "type", "") or ""),
                            directed=True,
                        )

        return ScenarioGraphResponse(
            nodes=list(nodes_by_id.values()),
            edges=list(edges_by_id.values()),
        )
