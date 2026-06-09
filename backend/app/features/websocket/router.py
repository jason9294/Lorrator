from typing import Annotated
from uuid import UUID

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
from app.core.realtime.websocket.envelopes import (
    ErrorEnvelope,
    TopicSubscriptionAckEnvelope,
    TopicSubscriptionAction,
    WsErrorCode,
)
from app.core.realtime.websocket.manager import WebSocketConnectionManager
from app.core.realtime.websocket.protocol import (
    ClientMessage,
    ClientMessageType,
    TopicPayload,
)
from app.core.realtime.websocket.ticket_store import WebSocketTicketStore
from app.core.realtime.websocket.topics import WsTopic

from .schemas import WsTicketResponse
from .topic_auth import can_subscribe_to_topic

_WS_TICKET_TTL_SECONDS = 60

router = APIRouter(prefix="/websocket", tags=["websocket"])


def _provide_ws_ticket_store(ws: WebSocket) -> WebSocketTicketStore:
    return ws.app.state.ws_ticket_store


def _provide_ws_connection_manager(ws: WebSocket) -> WebSocketConnectionManager:
    return ws.app.state.ws_connection_manager


async def _send_error(websocket: WebSocket, code: WsErrorCode) -> None:
    await websocket.send_json(ErrorEnvelope(code=code).format())


async def _send_subscription_ack(
    websocket: WebSocket,
    *,
    topic: str,
    action: TopicSubscriptionAction,
    ok: bool = True,
) -> None:
    await websocket.send_json(
        TopicSubscriptionAckEnvelope(topic=topic, action=action, ok=ok).format()
    )


async def _handle_client_message(
    *,
    websocket: WebSocket,
    connection_id: UUID,
    user_id: UUID,
    manager: WebSocketConnectionManager,
    message: ClientMessage,
) -> None:
    if message.type == ClientMessageType.SUBSCRIBE:
        try:
            payload = TopicPayload.model_validate(message.payload)
        except ValidationError:
            await _send_error(websocket, "invalid_envelope")
            return
        if not await can_subscribe_to_topic(user_id, payload.topic):
            await _send_subscription_ack(
                websocket,
                topic=payload.topic,
                action="subscribe",
                ok=False,
            )
            return
        manager.subscribe(connection_id, payload.topic)
        await _send_subscription_ack(
            websocket,
            topic=payload.topic,
            action="subscribe",
        )
        return

    if message.type == ClientMessageType.UNSUBSCRIBE:
        try:
            payload = TopicPayload.model_validate(message.payload)
        except ValidationError:
            await _send_error(websocket, "invalid_envelope")
            return
        manager.unsubscribe(connection_id, payload.topic)
        await _send_subscription_ack(
            websocket,
            topic=payload.topic,
            action="unsubscribe",
        )
        return

    await _send_error(websocket, "unknown_message_type")


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
    ticket_store: Annotated[WebSocketTicketStore, Depends(_provide_ws_ticket_store)],
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

    connection = await manager.connect(user_id, websocket)
    documents_topic = WsTopic.user_documents(user_id)
    manager.subscribe(connection.id, documents_topic)
    await _send_subscription_ack(
        websocket,
        topic=documents_topic,
        action="subscribe",
    )

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
                message = ClientMessage.model_validate_json(text)
            except ValidationError:
                await _send_error(websocket, "invalid_envelope")
                continue
            await _handle_client_message(
                websocket=websocket,
                connection_id=connection.id,
                user_id=user_id,
                manager=manager,
                message=message,
            )
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(connection.id)
