from logging import getLogger
from uuid import UUID, uuid4

from fastapi import WebSocket

from app.core.realtime.websocket.envelopes import BaseEnvelope

from .types import WebsocketConnection

logger = getLogger(__name__)

_ws_connection_manager: "WebSocketConnectionManager | None" = None


def set_ws_connection_manager(manager: "WebSocketConnectionManager") -> None:
    global _ws_connection_manager
    _ws_connection_manager = manager


def get_ws_connection_manager() -> "WebSocketConnectionManager":
    if _ws_connection_manager is None:
        raise RuntimeError("WebSocketConnectionManager 尚未初始化（lifespan）")
    return _ws_connection_manager


class WebSocketConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[UUID, WebsocketConnection] = {}
        self.topic_connections: dict[str, set[UUID]] = {}

    async def connect(
        self,
        user_id: UUID,
        websocket: WebSocket,
    ) -> WebsocketConnection:
        # accept the websocket connection and add it to the connection pool
        await websocket.accept()

        connection = WebsocketConnection(
            id=uuid4(),
            user_id=user_id,
            websocket=websocket,
        )

        self.connections[connection.id] = connection
        return connection

    def disconnect(self, connection_id: UUID) -> None:
        # remove the connection from the connection pool and unsubscribe from all topics
        connection = self.connections.pop(connection_id, None)

        if connection is None:
            return

        for topic in list(connection.subscriptions):
            self.unsubscribe(connection_id, topic)

    def subscribe(self, connection_id: UUID, topic: str) -> None:
        logger.info(f"Subscribing connection {connection_id} to topic {topic}")

        connection = self.connections.get(connection_id)

        if connection is None:
            return

        connection.subscriptions.add(topic)

        if topic not in self.topic_connections:
            self.topic_connections[topic] = set()

        self.topic_connections[topic].add(connection_id)

    def unsubscribe(self, connection_id: UUID, topic: str) -> None:
        logger.info(f"Unsubscribing connection {connection_id} from topic {topic}")

        connection = self.connections.get(connection_id)

        if connection is not None:
            connection.subscriptions.discard(topic)

        connection_ids = self.topic_connections.get(topic)

        if connection_ids is not None:
            connection_ids.discard(connection_id)

            if not connection_ids:
                self.topic_connections.pop(topic, None)

    async def send_to_topic(self, topic: str, envelope: BaseEnvelope) -> None:
        logger.info(f"Sending envelope {envelope._type.value} to topic {topic}")

        connection_ids = list(self.topic_connections.get(topic, set()))

        stale_connections: list[UUID] = []

        for connection_id in connection_ids:
            connection = self.connections.get(connection_id)

            if connection is None:
                continue

            try:
                await connection.websocket.send_json(envelope.format())
            except Exception:
                stale_connections.append(connection_id)

        for connection_id in stale_connections:
            self.disconnect(connection_id)
