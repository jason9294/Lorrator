from dataclasses import dataclass, field
from uuid import UUID

from fastapi import WebSocket


@dataclass
class WebsocketConnection:
    id: UUID
    user_id: UUID
    websocket: WebSocket
    subscriptions: set[str] = field(default_factory=set)
