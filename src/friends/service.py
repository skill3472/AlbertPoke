from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from friends.schemas import Friend


def are_mutual_friends(db: Session, user_a_id: int, user_b_id: int) -> bool:
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
