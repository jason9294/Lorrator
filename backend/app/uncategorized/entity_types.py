from typing import Literal

from pydantic import BaseModel


class Event(BaseModel):
    """event of scenario"""


class Location(BaseModel):
    """location of scenario"""


class Item(BaseModel):
    """item of scenario"""


class Ending(BaseModel):
    """ending of scenario"""

    ending_type: Literal["good", "bad", "normal", "hidden", "other"]
