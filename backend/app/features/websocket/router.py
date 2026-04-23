from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import ValidationError

from app.core.deps import JWTDependency
from app.core.websocket.manager import WebSocketConnectionManager
from app.core.websocket.schemas import WsMessageEnvelope, WsTicketResponse
from app.core.websocket.ticket_store import WsTicketStore

_WS_TICKET_TTL_SECONDS = 60

router = APIRouter(prefix="/websocket", tags=["websocket"])


def _provide_ws_ticket_store(ws: WebSocket) -> WsTicketStore:
    return ws.app.state.ws_ticket_store


def _provide_ws_connection_manager(ws: WebSocket) -> WebSocketConnectionManager:
    return ws.app.state.ws_connection_manager


async def _send_error(websocket: WebSocket, code: str) -> None:
    await websocket.send_json(
        WsMessageEnvelope(type="error", payload={"code": code}).model_dump()
    )


@router.post(
    path="/ticket",
    summary="以 access token 換取一次性 WebSocket 連線票證",
)
async def issue_ws_ticket(
    jwt: JWTDependency,
    request: Request,
) -> WsTicketResponse:
    store = request.app.state.ws_ticket_store
    ticket = await store.issue(jwt.sub, ttl_seconds=_WS_TICKET_TTL_SECONDS)
    return WsTicketResponse(ticket=ticket, expires_in_seconds=_WS_TICKET_TTL_SECONDS)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_store: Annotated[WsTicketStore, Depends(_provide_ws_ticket_store)],
    manager: Annotated[
        WebSocketConnectionManager, Depends(_provide_ws_connection_manager)
    ],
    ticket: Annotated[str | None, Query()] = None,
) -> None:
    if not ticket:
        await websocket.close(code=1008, reason="missing ticket")
        return
    user_id = await ticket_store.consume(ticket)
    if user_id is None:
        await websocket.close(code=1008, reason="invalid or expired ticket")
        return
    await manager.connect(user_id, websocket)
    try:
        while True:
            raw = await websocket.receive()
            if raw.get("type") == "websocket.disconnect":
                break
            if raw.get("type") != "websocket.receive":
                continue
            text = raw.get("text")
            if text is None:
                await _send_error(websocket, "expected_text_frame")
                continue
            try:
                WsMessageEnvelope.model_validate_json(text)
            except ValidationError:
                await _send_error(websocket, "invalid_envelope")
                continue
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(user_id, websocket)
