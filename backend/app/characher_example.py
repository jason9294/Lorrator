from enum import StrEnum
from uuid import UUID, uuid7

from pydantic import BaseModel, Field, computed_field


class OccupationFeatureType(StrEnum):
    """COC 職業特性"""

    EDU = "EDU"
    EDU_STR = "EDU_STR"
    EDU_DEX = "EDU_DEX"
    EDU_APP = "EDU_APP"
    EDU_POW = "EDU_POW"


class CoCSkillType(StrEnum):
    """COC 技能類型"""

    STANDARD = "STANDARD"  # 標準技能
    DERIVED = "DERIVED"  # 衍生技能
    CUSTOM = "CUSTOM"  # 自訂技能


class CoCSkillCategory(StrEnum):
    """COC 技能分類"""

    NEGOTIATION = "NEGOTIATION"  # 溝通
    INVESTIGATION = "INVESTIGATION"  # 調查
    LANGUAGE = "LANGUAGE"  # 語言
    MEDICAL = "MEDICAL"  # 醫療
    PILOT = "PILOT"  # 特殊駕駛
    SURVIVAL = "SURVIVAL"  # 生存
    ART_AND_CRAFT = "ART_AND_CRAFT"  # 藝術與工藝
    SCIENCE = "SCIENCE"  # 科學
    CUSTOM = "CUSTOM"  # 自訂


class CoCSkillAdjustmentType(StrEnum):
    """COC 技能調整來源"""

    GROWTH = "GROWTH"  # 成長點數
    CUSTOM = "CUSTOM"  # 自訂情境


class SkillAdjustment(BaseModel):
    type: CoCSkillAdjustmentType
    value: int
    note: str


class CharacterSkill(BaseModel):
    type: CoCSkillType
    category: CoCSkillCategory
    name: str
    base_value: int
    occupation_value: int
    interest_value: int
    adjustments: list[SkillAdjustment]

    @property
    @computed_field
    def total_value(self) -> int:
        return (
            self.base_value
            + self.occupation_value
            + self.interest_value
            + sum(adjustment.value for adjustment in self.adjustments)
        )


class CharacterExample(BaseModel):
    ## metadata
    id: UUID = Field(default_factory=uuid7)
    name: str
    owner_id: UUID

    ## character information

    occupation: str = ""  # 角色職業
    occupational_features: OccupationFeatureType = OccupationFeatureType.EDU

    age: int = 0
    gender: str = ""

    residence: str = ""  # 角色所在地
    birthplace: str = ""  # 角色出生地

    description: str = ""  # 角色描述

    # 當前屬性
    hp: int = 0
    mp: int = 0
    san: int = 0
    luck: int = 0

    # Characteristics 特徵
    strength: int = 0
    constitution: int = 0
    size: int = 0
    dexterity: int = 0
    appearance: int = 0
    intelligence: int = 0
    power: int = 0
    education: int = 0

    believer: bool = False  # 神話相信者
    cthulhu_mythos: int = 0

    # background 背景
    # 思念與信念
    ideology_beliefs: str = ""
    # 重要之人
    significant_people: str = ""
    # 意義非凡之地
    meaningful_locations: str = ""
    # 寶貴之物
    treasured_possessions: str = ""
    # 特點
    traits: str = ""
    bonds: str = ""  # 羈絆

    skills: list[CharacterSkill]
    skill_adjustments: list[SkillAdjustment]
