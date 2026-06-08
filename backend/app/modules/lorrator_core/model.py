from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    type: Literal["gm_narration", "npc_dialogue", "npc_action"]
    content: str
