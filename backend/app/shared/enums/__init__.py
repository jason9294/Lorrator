from enum import Enum, StrEnum


class GameSystem(str, Enum):
    COC = "COC"
    DND = "DND"


class ScenarioStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class RoomStatus(Enum):
    PREPARING = "PREPARING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


class RoomMessageRole(StrEnum):
    AGENT = "AGENT"
    PLAYER = "PLAYER"
    SYSTEM = "SYSTEM"


class RoomMessageType(StrEnum):
    CHAT = "CHAT"
    DICE = "DICE"
    DEBUG = "DEBUG"


class DocumentStatus(Enum):
    READY = "READY"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class GraphEntityType(StrEnum):
    CHUNK = "CHUNK"

    LOCATION = "LOCATION"  # 地點
    CHARACTER = "CHARACTER"  # 角色 (NPC、怪物)
    FACTION = "FACTION"  # 陣營、組織、家族、教派、公會、政府機構
    EVENT = "EVENT"  # 已發生或將發生的重要事件
    ITEM = "ITEM"  # 物品
    SAN_CHECK = "SAN_CHECK"  # 理智檢定


class GraphRelationshipType(StrEnum):
    MENTIONS = "MENTIONS"
    RELATES_TO = "RELATES_TO"
    SIMILAR_TO = "SIMILAR_TO"


class ProcessingRunStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProcessingStepId(StrEnum):
    PREPARE = "prepare"
    CLEAR_GRAPH = "clear_graph"
    CHUNK = "chunk"
    ENTITY_EXTRACTION = "entity_extraction"
    GRAPH_BUILD = "graph_build"
    ENTITY_EMBEDDING = "entity_embedding"
