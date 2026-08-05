from pydantic import BaseModel, ConfigDict

from friends.models import FriendBrief


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    password: str
    altcha: str  # solved ALTCHA challenge payload, base64-encoded


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)  # lets Pydantic read SQLAlchemy objects

    id: int


class UserWithFriends(UserRead):
    friends: list[FriendBrief] = []


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
