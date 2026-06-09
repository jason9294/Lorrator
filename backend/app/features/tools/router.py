from fastapi import APIRouter, Depends

from .schemas.requests import ChunkTextRequest, EntityGroupRequest
from .schemas.responses import ChunkTextResponse
from .services import (
    ChunkPlainTextService,
    EntityExtractToolService,
    EntityGroupToolService,
)

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post(
    path="/chunk-text",
    response_model=ChunkTextResponse,
    summary="將純文字分塊（token-based）",
)
async def chunk_plain_text(
    body: ChunkTextRequest,
    svc: ChunkPlainTextService = Depends(),
) -> ChunkTextResponse:
    return await svc.execute(body)


@router.post(
    path="/entity-extract",
    summary="提取實體",
)
async def entity_extract_tool(
    text: str,
    svc: EntityExtractToolService = Depends(),
):
    return await svc.execute(text)


@router.post(
    path="/entity-group",
    summary="實體分群",
)
async def entity_group_tool(
    body: EntityGroupRequest,
    svc: EntityGroupToolService = Depends(),
):
    return await svc.execute(body.chunks, body.entities)
