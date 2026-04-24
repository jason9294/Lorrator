from uuid import UUID

from app.db.uow import UnitOfWorkDependency
from app.features.characters.schemas.coc_schema import (
    CharacterSkill,
    CoCCharacterData,
    CoCSkillCategory,
    CoCSkillType,
)
from app.features.characters.schemas.requests import CreateCharacterRequest
from app.features.characters.schemas.responses import CharacterDetailResponse
from app.shared.enums import GameSystem

from .._utils import parse_character_data


def _make_skills(
    category: CoCSkillCategory, entries: list[tuple[str, int]]
) -> list[CharacterSkill]:
    return [
        CharacterSkill(
            type=CoCSkillType.STANDARD,
            category=category,
            name=name,
            base_value=base,
        )
        for name, base in entries
    ]


def default_coc_character_data() -> CoCCharacterData:
    C = CoCSkillCategory

    skills = [
        *_make_skills(C.LANGUAGE, [("母語", 0)]),
        *_make_skills(
            C.MEDICAL,
            [
                ("急救", 30),
                ("醫學", 1),
                ("心理分析", 1),
            ],
        ),
        *_make_skills(
            C.NEGOTIATION,
            [
                ("魅惑", 15),
                ("話術", 5),
                ("說服", 10),
                ("恐嚇", 15),
                ("心理學", 1),
            ],
        ),
        *_make_skills(
            C.INVESTIGATION,
            [
                ("偵查", 25),
                ("聆聽", 20),
                ("追蹤", 10),
                ("圖書館使用", 20),
            ],
        ),
        *_make_skills(
            C.COMBAT,
            [
                ("閃避", 0),
                ("鬥毆", 25),
            ],
        ),
        *_make_skills(
            C.CUSTOM,
            [
                ("催眠", 1),
                ("讀唇", 1),
                ("爆破", 1),
                ("炮術", 1),
                ("動物訓養", 5),
                ("潛水", 1),
            ],
        ),
        *_make_skills(
            C.OCCUPATION,
            [
                ("電器維修", 10),
                ("電子學", 1),
                ("電腦使用", 5),
                ("人類學", 1),
                ("考古學", 1),
                ("歷史", 5),
                ("會計", 5),
                ("估價", 5),
                ("法律", 5),
                ("機械維修", 10),
                ("自然學", 10),
                ("神祕學", 5),
            ],
        ),
        *_make_skills(
            C.SURVIVAL,
            [
                ("鎖匠", 1),
                ("巧手", 10),
                ("潛行", 20),
                ("喬裝", 5),
                ("生存", 10),
            ],
        ),
        *_make_skills(
            C.CUSTOM,
            [
                ("信用評級", 0),
                ("克蘇魯神話", 0),
            ],
        ),
        *_make_skills(
            C.MOVEMENT,
            [
                ("跳躍", 20),
                ("攀爬", 15),
                ("騎術", 5),
                ("游泳", 20),
                ("投擲", 20),
                ("導航", 10),
                ("汽車駕駛", 20),
                ("重型機械", 1),
            ],
        ),
    ]

    return CoCCharacterData(skills=skills)


class CreateCharacterService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(
        self, body: CreateCharacterRequest, owner_id: UUID
    ) -> CharacterDetailResponse:
        data = {}
        if body.game_system == GameSystem.COC:
            data = default_coc_character_data()

        character = await self._uow.character_repo.create(
            owner_id=owner_id,
            name=body.name,
            game_system=body.game_system,
            data=data.model_dump(),  # type: ignore[union-attr]
        )

        return CharacterDetailResponse(
            id=character.id,
            owner_id=character.owner_id,
            name=character.name,
            game_system=character.game_system,
            created_at=character.created_at,
            updated_at=character.updated_at,
            data=parse_character_data(character.game_system, character.data),
        )
