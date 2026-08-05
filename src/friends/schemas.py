from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from common.schemas import Base


class Friend(Base):
    __tablename__ = "friends"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    friend_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
