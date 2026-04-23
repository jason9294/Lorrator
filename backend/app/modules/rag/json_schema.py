from pydantic import BaseModel


class _Entity(BaseModel):
    name: str
    type: str
    description: str


class _Relationship(BaseModel):
    source_name: str
    target_name: str
    type: str
    description: str


class ExtractedEntities(BaseModel):
    entities: list[_Entity]
    relationships: list[_Relationship]
