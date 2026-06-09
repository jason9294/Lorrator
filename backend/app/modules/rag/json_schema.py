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


class SummaryRound(BaseModel):
    summaries: list[str] | None


class EntityGroupChunk(BaseModel):
    chunk_id: str
    content: str


class EntityGroupEntity(BaseModel):
    entity_id: str
    chunk_id: str
    name: str
    description: str


class EntityGroup(BaseModel):
    entity_groups: list[list[str]]
