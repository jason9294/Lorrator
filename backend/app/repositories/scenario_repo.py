from uuid import UUID

from sqlmodel import or_, select

from app.models import ScenarioModel
from app.shared.enums import ScenarioStatus

from ._base_repo import BaseRepository


class ScenarioRepository(BaseRepository):
    async def list_all(self) -> list[ScenarioModel]:
        statement = select(ScenarioModel).order_by(ScenarioModel.name)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_visible_to_user(self, user_id: UUID) -> list[ScenarioModel]:
        """回傳已發布的劇本 + 當前使用者自己的草稿"""
        statement = (
            select(ScenarioModel)
            .where(
                or_(
                    ScenarioModel.status == ScenarioStatus.PUBLISHED,
                    ScenarioModel.creator_id == user_id,
                )
            )
            .order_by(ScenarioModel.name)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_id(self, scenario_id: UUID) -> ScenarioModel | None:
        statement = select(ScenarioModel).where(ScenarioModel.id == scenario_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create(
        self,
        *,
        name: str,
        description: str | None,
        system: str,
        creator_id: UUID,
        min_players: int | None = None,
        max_players: int | None = None,
        min_hours: float | None = None,
        max_hours: float | None = None,
    ) -> ScenarioModel:
        scenario = ScenarioModel(
            name=name,
            description=description,
            system=system,
            creator_id=creator_id,
            min_players=min_players,
            max_players=max_players,
            min_hours=min_hours,
            max_hours=max_hours,
        )
        self.session.add(scenario)
        await self.session.flush()
        return scenario

    async def update(
        self,
        scenario: ScenarioModel,
        *,
        name: str | None = None,
        description: str | None = None,
        system: str | None = None,
        min_players: int | None = None,
        max_players: int | None = None,
        min_hours: float | None = None,
        max_hours: float | None = None,
    ) -> ScenarioModel:
        if name is not None:
            scenario.name = name
        if description is not None:
            scenario.description = description
        if system is not None:
            scenario.system = system
        if min_players is not None:
            scenario.min_players = min_players
        if max_players is not None:
            scenario.max_players = max_players
        if min_hours is not None:
            scenario.min_hours = min_hours
        if max_hours is not None:
            scenario.max_hours = max_hours
        self.session.add(scenario)
        await self.session.flush()
        return scenario

    async def publish(self, scenario: ScenarioModel) -> ScenarioModel:
        scenario.status = ScenarioStatus.PUBLISHED
        self.session.add(scenario)
        await self.session.flush()
        return scenario


def provide_scenario_repo_cls() -> type[ScenarioRepository]:
    return ScenarioRepository
