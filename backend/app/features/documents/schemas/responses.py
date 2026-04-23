from uuid import UUID

from pydantic import BaseModel

from app.shared.enums import DocumentStatus


class DocumentMarkdownResponse(BaseModel):
    content: str


class ProcessDocumentResponse(BaseModel):
    document_id: UUID
    status: DocumentStatus
    message: str
    entities: list
    relationships: list
