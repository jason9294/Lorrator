from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.deps import JWTDependency

from .schemas.requests import JoinRoomRequest, SendMessageRequest
from .schemas.responses import RoomDetailResponse, RoomMessageResponse
from .services import (
    GetRoomService,
    JoinRoomService,
    KickParticipantService,
    ListRoomMessagesService,
    RegenerateInviteService,
    SendRoomMessageService,
    SetReadyService,
    StartSessionService,
)

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get(
    path="/{room_id}",
    response_model=RoomDetailResponse,
    summary="取得房間詳情（需為參與者）",
)
async def get_room(
    room_id: UUID,
    jwt: JWTDependency,
    svc: GetRoomService = Depends(),
) -> RoomDetailResponse:
    return await svc.execute(room_id, jwt.sub)


@router.post(
    path="/join",
    response_model=RoomDetailResponse,
    summary="透過邀請碼加入房間",
)
async def join_room(
    body: JoinRoomRequest,
    jwt: JWTDependency,
    svc: JoinRoomService = Depends(),
) -> RoomDetailResponse:
    return await svc.execute(body, jwt.sub)


@router.post(
    path="/{room_id}/invite-code/regenerate",
    response_model=RoomDetailResponse,
    summary="重新生成邀請碼（僅房主）",
)
async def regenerate_invite_code(
    room_id: UUID,
    jwt: JWTDependency,
    svc: RegenerateInviteService = Depends(),
) -> RoomDetailResponse:
    return await svc.execute(room_id, jwt.sub)


@router.delete(
    path="/{room_id}/participants/{user_id}",
    response_model=RoomDetailResponse,
    summary="踢出參與者（僅房主）",
)
async def kick_participant(
    room_id: UUID,
    user_id: UUID,
    jwt: JWTDependency,
    svc: KickParticipantService = Depends(),
) -> RoomDetailResponse:
    return await svc.execute(room_id, user_id, jwt.sub)


@router.post(
    path="/{room_id}/ready",
    response_model=RoomDetailResponse,
    summary="設定自己的準備狀態",
)
async def set_ready(
    room_id: UUID,
    is_ready: bool,
    jwt: JWTDependency,
    svc: SetReadyService = Depends(),
) -> RoomDetailResponse:
    return await svc.execute(room_id, is_ready, jwt.sub)


@router.post(
    path="/{room_id}/start",
    response_model=RoomDetailResponse,
    summary="開始跑團（僅房主，所有人須已就緒）",
)
async def start_session(
    room_id: UUID,
    jwt: JWTDependency,
    svc: StartSessionService = Depends(),
) -> RoomDetailResponse:
    return await svc.execute(room_id, jwt.sub)


@router.get(
    path="/{room_id}/messages",
    response_model=list[RoomMessageResponse],
    summary="取得聊天記錄（僅跑團進行中）",
)
async def list_room_messages(
    room_id: UUID,
    jwt: JWTDependency,
    svc: ListRoomMessagesService = Depends(),
) -> list[RoomMessageResponse]:
    return await svc.execute(room_id, jwt.sub)


@router.post(
    path="/{room_id}/messages",
    response_model=RoomMessageResponse,
    summary="在房間內傳送訊息",
)
async def send_room_message(
    room_id: UUID,
    body: SendMessageRequest,
    jwt: JWTDependency,
    svc: SendRoomMessageService = Depends(),
) -> RoomMessageResponse:
    return await svc.execute(room_id, body, jwt.sub)
