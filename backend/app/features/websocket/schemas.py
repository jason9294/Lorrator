from pydantic import BaseModel


class WsTicketResponse(BaseModel):
    ticket: str
    expires_in_seconds: int
