from pydantic import BaseModel


class RankedDocument(BaseModel):
    rank: int
    score: float
    document: str


class RerankResponse(BaseModel):
    ranked_documents: list[RankedDocument]
