from pydantic import BaseModel, Field


class RerankRequest(BaseModel):
    query: str = Field(..., description="查詢字串")
    documents: list[str] = Field(..., description="待排序的文件清單", min_length=1)
