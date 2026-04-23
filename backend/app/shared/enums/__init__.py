from enum import Enum


class ScenarioStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class RoomStatus(Enum):
    PREPARING = "PREPARING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


class DocumentStatus(Enum):
    READY = "READY"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
