from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=32000)


class JoinRoomRequest(BaseModel):
    invite_code: str = Field(min_length=1, max_length=16)
