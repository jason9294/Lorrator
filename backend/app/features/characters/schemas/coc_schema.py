from enum import StrEnum

from pydantic import BaseModel, computed_field


class OccupationFeatureType(StrEnum):
    """COC 職業技能點計算方式"""

    EDU = "EDU"
    EDU_STR = "EDU_STR"
    EDU_DEX = "EDU_DEX"
    EDU_APP = "EDU_APP"
    EDU_POW = "EDU_POW"


class CoCSkillType(StrEnum):
    """COC 技能類型"""

    STANDARD = "STANDARD"
    DERIVED = "DERIVED"
    CUSTOM = "CUSTOM"


class CoCSkillCategory(StrEnum):
    """COC 技能分類"""

    NEGOTIATION = "NEGOTIATION"
    INVESTIGATION = "INVESTIGATION"
    LANGUAGE = "LANGUAGE"
    MEDICAL = "MEDICAL"
    PILOT = "PILOT"
    SURVIVAL = "SURVIVAL"
    ART_AND_CRAFT = "ART_AND_CRAFT"
    SCIENCE = "SCIENCE"
    CUSTOM = "CUSTOM"


class CoCSkillAdjustmentType(StrEnum):
    """COC 技能調整來源"""

    GROWTH = "GROWTH"
    CUSTOM = "CUSTOM"


class SkillAdjustment(BaseModel):
    type: CoCSkillAdjustmentType
    value: int
    note: str = ""


class CharacterSkill(BaseModel):
    type: CoCSkillType
    category: CoCSkillCategory
    name: str
    base_value: int = 0
    occupation_value: int = 0
    interest_value: int = 0
    adjustments: list[SkillAdjustment] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_value(self) -> int:
        return (
            self.base_value
            + self.occupation_value
            + self.interest_value
            + sum(adj.value for adj in self.adjustments)
        )


class CoCCharacterData(BaseModel):
    """COC 7th Edition 角色資料（存入 JSONB）"""

    # 基本資訊
    occupation: str = ""
    occupational_features: OccupationFeatureType = OccupationFeatureType.EDU
    age: int = 0
    gender: str = ""
    residence: str = ""
    birthplace: str = ""
    description: str = ""

    # 當前屬性
    hp: int = 0
    mp: int = 0
    san: int = 0
    luck: int = 0

    # 特徵值（Characteristics）
    strength: int = 0
    constitution: int = 0
    size: int = 0
    dexterity: int = 0
    appearance: int = 0
    intelligence: int = 0
    power: int = 0
    education: int = 0

    # 神話相關
    believer: bool = False
    cthulhu_mythos: int = 0

    # 背景故事
    ideology_beliefs: str = ""
    significant_people: str = ""
    meaningful_locations: str = ""
    treasured_possessions: str = ""
    traits: str = ""
    bonds: str = ""

    # 技能
    skills: list[CharacterSkill] = []
    skill_adjustments: list[SkillAdjustment] = []
