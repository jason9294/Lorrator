import httpx
from pydantic import BaseModel


class RankedDocument(BaseModel):
    rank: int
    score: float
    document: str


async def rerank(query: str, documents: list[str], url: str) -> list[RankedDocument]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url=f"{url}",
            json={"query": query, "documents": documents},
        )
        response.raise_for_status()
        return [RankedDocument(**doc) for doc in response.json()["ranked_documents"]]
