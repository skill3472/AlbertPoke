from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from common.schemas import Base
from settings.models import DEFAULT_USER_SETTINGS


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    poke_layout: Mapped[str] = mapped_column(
        String(10), default=DEFAULT_USER_SETTINGS.poke_layout
    )
