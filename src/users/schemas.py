from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.schemas import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    hashed_password: Mapped[str] = mapped_column(String(255))

    # NOTE People this user added as friends
    friends: Mapped[list["User"]] = relationship(
        secondary="friends",
        primaryjoin="User.id == Friend.user_id",
        secondaryjoin="User.id == Friend.friend_user_id",
        back_populates="friended_by",
    )

    # NOTE People who added this user as a friend
    friended_by: Mapped[list["User"]] = relationship(
        secondary="friends",
        primaryjoin="User.id == Friend.friend_user_id",
        secondaryjoin="User.id == Friend.user_id",
        back_populates="friends",
    )
