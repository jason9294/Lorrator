from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.deps import JWTDependency

from .schemas.requests import CreateRoomRequest, CreateScenarioRequest, UpdateScenarioRequest
from .schemas.responses import (
    DocumentResponse,
    RoomDetailResponse,
    ScenarioResponse,
)
from .services import (
    CreateRoomService,
    CreateScenarioService,
    GetScenarioGraphService,
    GetScenarioService,
    ListScenarioDocumentsService,
    ListScenariosService,
    PublishScenarioService,
    UpdateScenarioService,
    UploadScenarioDocumentService,
)

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post(
    path="",
    response_model=ScenarioResponse,
    summary="創建劇本",
)
async def create_scenario(
    body: CreateScenarioRequest,
    jwt: JWTDependency,
    svc: CreateScenarioService = Depends(),
) -> ScenarioResponse:
    return await svc.execute(body, jwt.sub)


@router.get(
    path="",
    response_model=list[ScenarioResponse],
    summary="列出所有可見劇本（已發布 + 自己的草稿）",
)
async def list_scenarios(
    jwt: JWTDependency,
    svc: ListScenariosService = Depends(),
) -> list[ScenarioResponse]:
    return await svc.execute(jwt.sub)


@router.get(
    path="/{scenario_id}",
    response_model=ScenarioResponse,
    summary="取得劇本詳情（草稿僅創作者可看）",
)
async def get_scenario(
    scenario_id: UUID,
    jwt: JWTDependency,
    svc: GetScenarioService = Depends(),
) -> ScenarioResponse:
    return await svc.execute(scenario_id, jwt.sub)


@router.patch(
    path="/{scenario_id}",
    response_model=ScenarioResponse,
    summary="編輯劇本（僅草稿可編輯）",
)
async def update_scenario(
    scenario_id: UUID,
    body: UpdateScenarioRequest,
    jwt: JWTDependency,
    svc: UpdateScenarioService = Depends(),
) -> ScenarioResponse:
    return await svc.execute(scenario_id, body, jwt.sub)


@router.post(
    path="/{scenario_id}/publish",
    response_model=ScenarioResponse,
    summary="發布劇本（發布後不可再編輯）",
)
async def publish_scenario(
    scenario_id: UUID,
    jwt: JWTDependency,
    svc: PublishScenarioService = Depends(),
) -> ScenarioResponse:
    return await svc.execute(scenario_id, jwt.sub)


@router.post(
    path="/{scenario_id}/documents",
    response_model=DocumentResponse,
    summary="在劇本中上傳文件",
)
async def upload_scenario_document(
    scenario_id: UUID,
    svc: UploadScenarioDocumentService = Depends(),
    file: UploadFile = File(...),
) -> DocumentResponse:
    content = await file.read()
    return await svc.execute(
        scenario_id,
        file_content=content,
        filename=file.filename,
        content_type=file.content_type,
    )


@router.get(
    path="/{scenario_id}/documents",
    response_model=list[DocumentResponse],
    summary="查看劇本中的文件",
)
async def list_scenario_documents(
    scenario_id: UUID,
    svc: ListScenarioDocumentsService = Depends(),
) -> list[DocumentResponse]:
    return await svc.execute(scenario_id)


@router.post(
    path="/{scenario_id}/rooms",
    response_model=RoomDetailResponse,
    summary="在已發布的劇本建立跑團房間",
)
async def create_room(
    scenario_id: UUID,
    body: CreateRoomRequest,
    jwt: JWTDependency,
    svc: CreateRoomService = Depends(),
) -> RoomDetailResponse:
    return await svc.execute(scenario_id, body, jwt.sub)


@router.get(
    path="/{scenario_id}/graph",
    summary="查看劇本的知識圖譜",
)
async def get_scenario_graph(
    scenario_id: UUID,
    svc: GetScenarioGraphService = Depends(),
):
    await svc.execute(scenario_id)
