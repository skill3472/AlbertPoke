from typing import Literal
from pydantic import BaseModel


class PokeResponse(BaseModel):
    user_id: int
    success: bool
    current_streak: int


class PokeStatus(BaseModel):
    can_poke: bool
    streak: int