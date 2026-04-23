from fastapi import APIRouter, Depends

from .schemas.requests import RerankRequest
from .schemas.responses import RerankResponse
from .services import RerankService

router = APIRouter(prefix="/reranker", tags=["reranker"])


@router.post("/rerank", summary="Cross-Encoder 重新排序")
async def rerank_endpoint(
    body: RerankRequest,
    svc: RerankService = Depends(),
) -> RerankResponse:
    return await svc.execute(body)
