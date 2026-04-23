from uuid import UUID

from sqlmodel import desc, select

from app.models import RoomMessageModel
from app.shared.enums import RoomMessageRole

from ._base_repo import BaseRepository


class RoomMessageRepository(BaseRepository):
    async def create(
        self, room_id: UUID, sender_id: UUID | None, role: RoomMessageRole, content: str
    ) -> RoomMessageModel:
        msg = RoomMessageModel(
            room_id=room_id, sender_id=sender_id, role=role, content=content
        )
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def list_by_room(self, room_id: UUID) -> list[RoomMessageModel]:
        statement = (
            select(RoomMessageModel)
            .where(RoomMessageModel.room_id == room_id)
            .order_by(desc(RoomMessageModel.created_at))
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())


def provide_room_message_repo_cls() -> type[RoomMessageRepository]:
    return RoomMessageRepository
