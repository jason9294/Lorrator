import asyncio
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from app.shared.utils.time_utils import datetime_utcnow


@dataclass(frozen=True, slots=True)
class _TicketRecord:
    user_id: UUID
    expires_at: datetime


class WsTicketStore:
    """MVP：記憶體一次性連線票證，之後可換成 Redis。"""

    def __init__(self) -> None:
        self._data: dict[str, _TicketRecord] = {}
        self._lock = asyncio.Lock()

    def _purge_expired_locked(self) -> None:
        now = datetime_utcnow()
        expired = [k for k, v in self._data.items() if v.expires_at < now]
        for k in expired:
            del self._data[k]

    async def issue(self, user_id: UUID, ttl_seconds: int = 60) -> str:
        token = secrets.token_urlsafe(32)
        async with self._lock:
            self._purge_expired_locked()
            self._data[token] = _TicketRecord(
                user_id=user_id,
                expires_at=datetime_utcnow() + timedelta(seconds=ttl_seconds),
            )
        return token

    async def consume(self, token: str) -> UUID | None:
        async with self._lock:
            self._purge_expired_locked()
            rec = self._data.pop(token, None)
            if rec is None:
                return None
            if rec.expires_at < datetime_utcnow():
                return None
            return rec.user_id
