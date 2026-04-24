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


class DocumentStatus(Enum):
    READY = "READY"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
