from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.websocket.manager import (
    WebSocketConnectionManager,
    set_ws_connection_manager,
)
from app.core.websocket.ticket_store import WsTicketStore
from app.db.graph import init_neo4j


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_neo4j()

    ws_manager = WebSocketConnectionManager()
    set_ws_connection_manager(ws_manager)
    app.state.ws_connection_manager = ws_manager
    app.state.ws_ticket_store = WsTicketStore()
    yield
