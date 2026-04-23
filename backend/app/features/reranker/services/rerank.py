from app.core.setting import get_settings
from app.modules.reranker import rerank

from ..schemas.requests import RerankRequest
from ..schemas.responses import RankedDocument, RerankResponse


class RerankService:
    async def execute(self, body: RerankRequest) -> RerankResponse:
        settings = get_settings()
        ranked_documents = await rerank(
            body.query, body.documents, settings.RERANKER_URL
        )
        return RerankResponse(
            ranked_documents=[
                RankedDocument(**doc.model_dump()) for doc in ranked_documents
            ]
        )
