from app.db.uow import AsyncUnitOfWork
from app.models import RoomModel
from app.features.rooms.schemas.responses import RoomDetailResponse, RoomParticipantResponse


async def build_room_detail(uow: AsyncUnitOfWork, room: RoomModel) -> RoomDetailResponse:
    participants = await uow.room_repo.list_participants(room.id)
    participant_responses = []
    for p in participants:
        user = await uow.user_repo.get_by_id(p.user_id)
        character = await uow.character_repo.get_by_id(p.character_id) if p.character_id else None
        participant_responses.append(
            RoomParticipantResponse(
                user_id=p.user_id,
                username=user.username if user else str(p.user_id),
                nickname=user.nickname if user else None,
                avatar_url=user.avatar_url if user else None,
                role=p.role,
                is_ready=p.is_ready,
                joined_at=p.joined_at,
                character_id=p.character_id,
                character_name=character.name if character else None,
            )
        )
    return RoomDetailResponse(
        id=room.id,
        scenario_id=room.scenario_id,
        host_id=room.host_id,
        name=room.name,
        description=room.description,
        status=room.status,
        invite_code=room.invite_code,
        participants=participant_responses,
    )
