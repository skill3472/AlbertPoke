from sqlalchemy.orm import Session

from settings.models import DEFAULT_USER_SETTINGS, UserSettingsRead, UserSettingsUpdate
from settings.schemas import UserSettings


def get_settings(db: Session, user_id: int) -> UserSettingsRead:
    """
    Reads a user's settings, falling back to defaults if they've never changed
    anything - a row only exists once a user has actually saved a preference.
    """
    row = db.get(UserSettings, user_id)
    if row is None:
        return DEFAULT_USER_SETTINGS
    return UserSettingsRead(poke_layout=row.poke_layout)


def update_settings(db: Session, user_id: int, update: UserSettingsUpdate) -> UserSettingsRead:
    row = db.get(UserSettings, user_id)
    if row is None:
        row = UserSettings(user_id=user_id, poke_layout=update.poke_layout)
        db.add(row)
    else:
        row.poke_layout = update.poke_layout
    db.commit()
    return UserSettingsRead(poke_layout=row.poke_layout)
