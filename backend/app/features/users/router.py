from fastapi import APIRouter, Depends

from .services import GetMeService, ListUsersService

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    path="",
    summary="...",
)
async def get_all(svc: ListUsersService = Depends()):
    return await svc.execute()


@router.get(
    path="/me",
    summary="...",
)
async def get_me(svc: GetMeService = Depends()):
    return await svc.execute()
