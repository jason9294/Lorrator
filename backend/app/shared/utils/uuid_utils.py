from uuid import UUID

from uuid_extensions import uuid7 as _uuid7


def uuid7() -> UUID:
    uuid = _uuid7(as_type=None)
    if not isinstance(uuid, UUID):
        raise ValueError("uuid7() returned a non-UUID value")
    return uuid
