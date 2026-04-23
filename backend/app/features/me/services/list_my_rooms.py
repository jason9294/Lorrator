from uuid import UUID

from app.db.uow import UnitOfWorkDependency

from ..schemas.responses import RoomResponse


class ListMyRoomsService:
    def __init__(self, uow: UnitOfWorkDependency) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID) -> list[RoomResponse]:
        rooms = await self._uow.room_repo.list_participating_rooms(user_id)
        return [RoomResponse.model_validate(room) for room in rooms]

