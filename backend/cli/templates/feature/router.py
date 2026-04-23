from fastapi import APIRouter

router = APIRouter(prefix="/router", tags=["router"])


@router.get(
    path="",
    summary="...",
)
async def get_all():
    return ...
