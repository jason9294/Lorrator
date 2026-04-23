from fastapi import APIRouter, Depends

from app.core.deps import JWTDependency

from .schemas.responses import RoomResponse
from .services import ListMyRoomsService

router = APIRouter(prefix="/me", tags=["me"])


@router.get(
    path="/rooms",
    response_model=list[RoomResponse],
    summary="查看自己參與的房間",
)
async def list_my_rooms(
    jwt: JWTDependency,
    svc: ListMyRoomsService = Depends(),
) -> list[RoomResponse]:
    return await svc.execute(jwt.sub)

