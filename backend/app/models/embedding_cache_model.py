from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from .mixin.timestamp import TimestampMixin


class EmbeddingCacheModel(TimestampMixin, SQLModel, table=True):
    """以原文雜湊為索引的快取列，用於略過重複的 embedding 呼叫。

    - `content_hash`：建議對 `source_text` 以 UTF-8 編碼後做 SHA-256，取 64 字元小寫十六進位字串。
    - `model_key`：embedding 設定識別（例如模型名稱與維度），與 `content_hash` 組成複合主鍵，避免不同模型共用同一雜湊。
    """

    __tablename__ = "embedding_caches"  # type: ignore

    content_hash: str = Field(max_length=64, primary_key=True)
    model_key: str = Field(max_length=128, primary_key=True)

    source_text: str = Field(sa_column=Column(Text, nullable=False))
    vector: Any = Field(sa_column=Column(Vector(1536), nullable=False))
