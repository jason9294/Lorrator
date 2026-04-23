import asyncio
from collections import defaultdict
from typing import Any
from uuid import UUID

from fastapi import WebSocket

from app.core.websocket.schemas import WsMessageEnvelope

_ws_connection_manager: "WebSocketConnectionManager | None" = None


def set_ws_connection_manager(manager: "WebSocketConnectionManager") -> None:
    global _ws_connection_manager
    _ws_connection_manager = manager


def get_ws_connection_manager() -> "WebSocketConnectionManager":
    if _ws_connection_manager is None:
        raise RuntimeError("WebSocketConnectionManager 尚未初始化（lifespan）")
    return _ws_connection_manager


class WebSocketConnectionManager:
    """依 user_id 管理多條連線，供各模組推送訊息。"""

    def __init__(self) -> None:
        self._by_user: dict[UUID, list[WebSocket]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._by_user[user_id].append(websocket)

    async def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self._by_user.get(user_id)
            if not conns:
                return
            try:
                conns.remove(websocket)
            except ValueError:
                return
            if not conns:
                del self._by_user[user_id]

    async def send_to_user(
        self,
        user_id: UUID,
        *,
        message_type: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        body = WsMessageEnvelope(
            type=message_type, payload=payload or {}
        ).model_dump()
        async with self._lock:
            sockets = list(self._by_user.get(user_id, ()))
        for ws in sockets:
            try:
                await ws.send_json(body)
            except Exception:
                await self.disconnect(user_id, ws)

    def user_connection_count(self, user_id: UUID) -> int:
        return len(self._by_user.get(user_id, ()))
