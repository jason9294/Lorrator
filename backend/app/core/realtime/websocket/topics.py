from uuid import UUID


class WsTopic:
    """WebSocket topic naming for pub/sub push."""

    ROOM_PREFIX = "rooms:"
    USER_DOCUMENTS_PREFIX = "users:"
    USER_DOCUMENTS_SUFFIX = ":documents"

    @classmethod
    def room(cls, room_id: UUID | str) -> str:
        return f"{cls.ROOM_PREFIX}{room_id}"

    @classmethod
    def user_documents(cls, user_id: UUID | str) -> str:
        return f"{cls.USER_DOCUMENTS_PREFIX}{user_id}{cls.USER_DOCUMENTS_SUFFIX}"

    @classmethod
    def parse_room_id(cls, topic: str) -> UUID | None:
        if not topic.startswith(cls.ROOM_PREFIX):
            return None
        try:
            return UUID(topic[len(cls.ROOM_PREFIX) :])
        except ValueError:
            return None

    @classmethod
    def parse_user_documents_user_id(cls, topic: str) -> UUID | None:
        if not topic.startswith(cls.USER_DOCUMENTS_PREFIX):
            return None
        if not topic.endswith(cls.USER_DOCUMENTS_SUFFIX):
            return None
        raw = topic[
            len(cls.USER_DOCUMENTS_PREFIX) : -len(cls.USER_DOCUMENTS_SUFFIX)
        ]
        try:
            return UUID(raw)
        except ValueError:
            return None

    @classmethod
    def is_user_documents(cls, topic: str) -> bool:
        return cls.parse_user_documents_user_id(topic) is not None
