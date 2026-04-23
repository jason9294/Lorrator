from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.deps import JWTDependency

from .schemas.requests import CreateCharacterRequest, UpdateCharacterRequest
from .schemas.responses import CharacterDetailResponse, CharacterResponse
from .services import (
    CreateCharacterService,
    DeleteCharacterService,
    GetCharacterService,
    ListCharactersService,
    UpdateCharacterService,
)

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get(
    path="",
    response_model=list[CharacterResponse],
    summary="取得我的角色列表",
)
async def list_characters(
    jwt: JWTDependency,
    svc: ListCharactersService = Depends(),
) -> list[CharacterResponse]:
    return await svc.execute(jwt.sub)


@router.post(
    path="",
    response_model=CharacterDetailResponse,
    status_code=201,
    summary="建立新角色",
)
async def create_character(
    body: CreateCharacterRequest,
    jwt: JWTDependency,
    svc: CreateCharacterService = Depends(),
) -> CharacterDetailResponse:
    return await svc.execute(body, jwt.sub)


@router.get(
    path="/{character_id}",
    response_model=CharacterDetailResponse,
    summary="取得角色詳情（含角色卡資料）",
)
async def get_character(
    character_id: UUID,
    jwt: JWTDependency,
    svc: GetCharacterService = Depends(),
) -> CharacterDetailResponse:
    return await svc.execute(character_id, jwt.sub)


@router.patch(
    path="/{character_id}",
    response_model=CharacterDetailResponse,
    summary="更新角色（名稱或角色卡資料）",
)
async def update_character(
    character_id: UUID,
    body: UpdateCharacterRequest,
    jwt: JWTDependency,
    svc: UpdateCharacterService = Depends(),
) -> CharacterDetailResponse:
    return await svc.execute(character_id, body, jwt.sub)


@router.delete(
    path="/{character_id}",
    status_code=204,
    summary="刪除角色",
)
async def delete_character(
    character_id: UUID,
    jwt: JWTDependency,
    svc: DeleteCharacterService = Depends(),
) -> None:
    return await svc.execute(character_id, jwt.sub)
