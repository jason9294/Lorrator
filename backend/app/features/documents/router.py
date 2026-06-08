from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.core.deps import JWTDependency

from .schemas.responses import DocumentMarkdownResponse, ProcessDocumentResponse
from .schemas.processing_pipeline import DocumentProcessingPipelineResponse
from .services import (
    DownloadOriginalDocumentService,
    GetDocumentMarkdownService,
    GetDocumentProcessingPipelineService,
    ProcessDocumentService,
    ReprocessDocumentService,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get(
    path="/{document_id}/md",
    response_model=DocumentMarkdownResponse,
    summary="查看指定文件的 Markdown 內容",
)
async def get_document_markdown(
    document_id: UUID,
    svc: GetDocumentMarkdownService = Depends(),
) -> DocumentMarkdownResponse:
    return await svc.execute(document_id)


@router.get(
    path="/{document_id}/download",
    response_class=FileResponse,
    summary="下載原始文件檔案",
)
async def download_original_document(
    document_id: UUID,
    svc: DownloadOriginalDocumentService = Depends(),
):
    result = await svc.execute(document_id)
    return FileResponse(
        path=result.path,
        media_type=result.media_type,
        filename=result.filename,
    )


@router.get(
    path="/{document_id}/processing-pipeline",
    response_model=DocumentProcessingPipelineResponse,
    summary="取得文件處理流程結果",
)
async def get_document_processing_pipeline(
    document_id: UUID,
    jwt: JWTDependency,
    svc: GetDocumentProcessingPipelineService = Depends(),
) -> DocumentProcessingPipelineResponse:
    return await svc.execute(document_id)


@router.post(
    path="/{document_id}/process",
    response_model=ProcessDocumentResponse,
    summary="處理文件（解析／索引等後續流程）",
)
async def process_document(
    document_id: UUID,
    jwt: JWTDependency,
    svc: ProcessDocumentService = Depends(),
) -> ProcessDocumentResponse:
    return await svc.execute(document_id)


@router.post(
    path="/{document_id}/reprocess",
    response_model=ProcessDocumentResponse,
    summary="重新處理文件（清除舊圖譜資料後重新解析）",
)
async def reprocess_document(
    document_id: UUID,
    jwt: JWTDependency,
    svc: ReprocessDocumentService = Depends(),
) -> ProcessDocumentResponse:
    return await svc.execute(document_id)
