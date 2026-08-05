from fastapi import APIRouter, Depends, Security
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from common.auth import get_current_user
from common.db import get_db
from friends.exceptions import CannotFriendSelfError
from friends.models import FriendAddResult, MutualFriendsResult
from friends.schemas import Friend
from users.exceptions import UserNotFoundError
from users.schemas import User

friends_router = APIRouter()


def _are_mutual_friends(db: Session, user_a_id: int, user_b_id: int) -> bool:
    """
    Checks whether two users have each added the other as a friend.

    Relies on (user_id, friend_user_id) being the `friends` table's primary key, so
    each half of the OR below is a direct primary-key lookup rather than a table scan.
    """
    stmt = select(func.count()).select_from(Friend).where(
        or_(
            and_(Friend.user_id == user_a_id, Friend.friend_user_id == user_b_id),
            and_(Friend.user_id == user_b_id, Friend.friend_user_id == user_a_id),
        )
    )
    return db.execute(stmt).scalar_one() == 2


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

    mutual = _are_mutual_friends(db, current_user.id, friend_user_id)
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
    return MutualFriendsResult(mutual=_are_mutual_friends(db, user_a_id, user_b_id))
