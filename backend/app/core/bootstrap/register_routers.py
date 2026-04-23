from fastapi import FastAPI

from app.features.auth.router import router as auth_router
from app.features.me.router import router as me_router
from app.features.websocket.router import router as websocket_router
from app.features.documents.router import router as documents_router
from app.features.reranker.router import router as reranker_router
from app.features.rooms.router import router as rooms_router
from app.features.scenarios.router import router as scenarios_router
from app.features.tools.router import router as tools_router
from app.features.users.router import router as users_router


def register_routers(app: FastAPI) -> None:
    app.include_router(websocket_router)
    app.include_router(auth_router)
    app.include_router(me_router)
    app.include_router(users_router)
    app.include_router(reranker_router)
    app.include_router(scenarios_router)
    app.include_router(documents_router)
    app.include_router(tools_router)
    app.include_router(rooms_router)
