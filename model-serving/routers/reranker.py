from fastapi import APIRouter
from pydantic import BaseModel, Field
from sentence_transformers.cross_encoder import CrossEncoder

router = APIRouter(prefix="/reranker", tags=["reranker"])

_model: CrossEncoder | None = None


class RerankRequest(BaseModel):
    query: str = Field(..., description="查詢字串")
    documents: list[str] = Field(..., description="待排序的文件清單", min_length=1)


class RankedDocument(BaseModel):
    rank: int
    score: float
    document: str


class RerankResponse(BaseModel):
    ranked_documents: list[RankedDocument]


def _get_model() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
    return _model


@router.post("/rerank", summary="Cross-Encoder 重新排序")
async def rerank_endpoint(body: RerankRequest) -> RerankResponse:
    pairs = [[body.query, doc] for doc in body.documents]
    scores: list[float] = _get_model().predict(pairs).tolist()

    ranked = sorted(
        zip(scores, body.documents),
        key=lambda x: x[0],
        reverse=True,
    )

    return RerankResponse(
        ranked_documents=[
            RankedDocument(rank=i + 1, score=score, document=doc)
            for i, (score, doc) in enumerate(ranked)
        ]
    )
