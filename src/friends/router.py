from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from common.auth import get_current_user
from common.db import get_db
from friends.exceptions import CannotFriendSelfError
from friends.models import FriendAddResult, FriendBrief, MutualFriendsResult
from friends.schemas import Friend
from friends.service import are_mutual_friends
from users.exceptions import UserNotFoundError
from users.schemas import User

friends_router = APIRouter()


@friends_router.get("/list")
def list_friends(current_user: User = Security(get_current_user)) -> list[FriendBrief]:
    """
    Lists the people the current user has added as friends.

    Returns:
        list[FriendBrief]: the current user's added friends
    """
    return [FriendBrief.model_validate(f) for f in current_user.friends]


@friends_router.post("/add/{friend_user_id}")
def add_friend(
    friend_user_id: int,
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> FriendAddResult:
    """
    Adds `friend_user_id` as a friend of the current user.

    Args:
        friend_user_id(int): id of the user to add as a friend

    Returns:
        FriendAddResult: the target user's id, and whether the friendship is now mutual
    """
    if friend_user_id == current_user.id:
        raise CannotFriendSelfError("You cannot add yourself as a friend.")

    friend = db.get(User, friend_user_id)
    if friend is None:
        raise UserNotFoundError(f"User with id: {friend_user_id} was not found.")

    existing = db.get(Friend, (current_user.id, friend_user_id))
    if existing is None:
        db.add(Friend(user_id=current_user.id, friend_user_id=friend_user_id))
        db.commit()

    mutual = are_mutual_friends(db, current_user.id, friend_user_id)
    return FriendAddResult(friend_id=friend_user_id, mutual=mutual)


@friends_router.get("/mutual/{user_a_id}/{user_b_id}")
def check_mutual_friends(
    user_a_id: int,
    user_b_id: int,
    db: Session = Depends(get_db),
) -> MutualFriendsResult:
    """
    Checks whether two users are mutual friends.

    Args:
        user_a_id(int): id of the first user
        user_b_id(int): id of the second user

    Returns:
        MutualFriendsResult: whether both users have added each other as friends
    """
    return MutualFriendsResult(mutual=are_mutual_friends(db, user_a_id, user_b_id))
