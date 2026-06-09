from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.realtime.websocket.topics import WsTopic
from app.db.sql import async_engine
from app.repositories.room_repo import RoomRepository


async def can_subscribe_to_topic(user_id: UUID, topic: str) -> bool:
    if WsTopic.is_user_documents(topic):
        topic_user_id = WsTopic.parse_user_documents_user_id(topic)
        return topic_user_id == user_id

    room_id = WsTopic.parse_room_id(topic)
    if room_id is not None:
        async with AsyncSession(async_engine) as session:
            repo = RoomRepository(session)
            participant = await repo.get_participant(room_id, user_id)
            return participant is not None

    return False
