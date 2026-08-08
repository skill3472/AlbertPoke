from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from common.auth import get_current_user
from common.db import get_db
from settings import service
from settings.models import UserSettingsRead, UserSettingsUpdate
from users.schemas import User

settings_router = APIRouter()


@settings_router.get("")
def get_settings(
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> UserSettingsRead:
    """
    Gets the current user's settings, or the defaults if they've never saved any.

    Returns:
        UserSettingsRead: the current user's settings
    """
    return service.get_settings(db, current_user.id)


@settings_router.put("")
def update_settings(
    update: UserSettingsUpdate,
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> UserSettingsRead:
    """
    Updates the current user's settings.

    Args:
        update(UserSettingsUpdate): the settings to save

    Returns:
        UserSettingsRead: the saved settings
    """
    return service.update_settings(db, current_user.id, update)
