from datetime import UTC, datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.schemas import Base
from users.schemas import User


class Poke(Base):
    __tablename__ = "pokes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    from_user: Mapped[User] = relationship(
        foreign_keys=[from_user_id],
    )
    to_user: Mapped[User] = relationship(
        foreign_keys=[to_user_id],
    )
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
