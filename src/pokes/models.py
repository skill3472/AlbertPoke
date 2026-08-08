from pydantic import BaseModel

from friends.models import FriendBrief


class PokeResponse(BaseModel):
    user_id: int
    success: bool
    current_streak: int


class PokeStatus(BaseModel):
    can_poke: bool
    streak: int
    mutual: bool
    cooldown_seconds: int


class PokeThread(BaseModel):
    user: FriendBrief
    streak: int
    can_poke: bool
    last_poke_mine: bool
    mutual: bool
    cooldown_seconds: int