import secrets
from uuid import UUID

from sqlmodel import col, select

from app.models import RoomModel
from app.models.links.room_participant_link import RoomParticipantLink
from app.shared.enums import RoomStatus

from ._base_repo import BaseRepository


class RoomRepository(BaseRepository):
    async def get_by_id(self, room_id: UUID) -> RoomModel | None:
        statement = select(RoomModel).where(RoomModel.id == room_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_invite_code(self, invite_code: str) -> RoomModel | None:
        statement = select(RoomModel).where(
            RoomModel.invite_code == invite_code.upper()
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create(
        self,
        scenario_id: UUID,
        host_id: UUID,
        name: str,
        description: str | None,
    ) -> RoomModel:
        room = RoomModel(
            scenario_id=scenario_id,
            host_id=host_id,
            name=name,
            description=description,
        )
        self.session.add(room)
        await self.session.flush()
        return room

    async def update_status(self, room: RoomModel, status: RoomStatus) -> RoomModel:
        room.status = status
        self.session.add(room)
        await self.session.flush()
        return room

    async def regenerate_invite_code(self, room: RoomModel) -> RoomModel:
        room.invite_code = secrets.token_hex(4).upper()
        self.session.add(room)
        await self.session.flush()
        return room

    async def add_participant(
        self, room_id: UUID, user_id: UUID, role: str
    ) -> RoomParticipantLink:
        link = RoomParticipantLink(room_id=room_id, user_id=user_id, role=role)
        self.session.add(link)
        await self.session.flush()
        return link

    async def get_participant(
        self, room_id: UUID, user_id: UUID
    ) -> RoomParticipantLink | None:
        statement = select(RoomParticipantLink).where(
            RoomParticipantLink.room_id == room_id,
            RoomParticipantLink.user_id == user_id,
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def list_participants(self, room_id: UUID) -> list[RoomParticipantLink]:
        statement = select(RoomParticipantLink).where(
            RoomParticipantLink.room_id == room_id
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def set_participant_ready(
        self, participant: RoomParticipantLink, is_ready: bool
    ) -> RoomParticipantLink:
        participant.is_ready = is_ready
        self.session.add(participant)
        await self.session.flush()
        return participant

    async def remove_participant(self, participant: RoomParticipantLink) -> None:
        await self.session.delete(participant)
        await self.session.flush()

    async def list_participating_rooms(self, user_id: UUID) -> list[RoomModel]:
        statement = (
            select(RoomModel)
            .join(
                RoomParticipantLink,
                col(RoomParticipantLink.room_id) == col(RoomModel.id),
            )
            .where(RoomParticipantLink.user_id == user_id)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())


def provide_room_repo_cls() -> type[RoomRepository]:
    return RoomRepository
