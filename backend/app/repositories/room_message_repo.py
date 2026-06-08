from uuid import UUID

from sqlmodel import asc, select

from app.models import RoomMessageModel
from app.shared.enums import RoomMessageRole, RoomMessageType

from ._base_repo import BaseRepository


class RoomMessageRepository(BaseRepository):
    async def create(
        self,
        room_id: UUID,
        sender_id: UUID | None,
        role: RoomMessageRole,
        content: str,
        type: RoomMessageType = RoomMessageType.CHAT,
        detail: str | None = None,
    ) -> RoomMessageModel:
        msg = RoomMessageModel(
            room_id=room_id,
            sender_id=sender_id,
            role=role,
            type=type,
            content=content,
            detail=detail,
        )
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def list_by_room(self, room_id: UUID) -> list[RoomMessageModel]:
        statement = (
            select(RoomMessageModel)
            .where(RoomMessageModel.room_id == room_id)
            .order_by(asc(RoomMessageModel.created_at))
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())


def provide_room_message_repo_cls() -> type[RoomMessageRepository]:
    return RoomMessageRepository
