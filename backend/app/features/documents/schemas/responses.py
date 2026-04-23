from uuid import UUID

from pydantic import BaseModel


class DocumentMarkdownResponse(BaseModel):
    content: str


class ProcessDocumentResponse(BaseModel):
    document_id: UUID
    message: str = "TODO: document processing not implemented"
    entities: list
    relationships: list
