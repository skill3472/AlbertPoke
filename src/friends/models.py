from pydantic import BaseModel, ConfigDict


class FriendBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class FriendAddResult(BaseModel):
    friend_id: int
    mutual: bool


class MutualFriendsResult(BaseModel):
    mutual: bool
