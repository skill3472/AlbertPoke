from pydantic import BaseModel

from settings.constants import PokeLayout


class UserSettingsRead(BaseModel):
    poke_layout: PokeLayout


class UserSettingsUpdate(BaseModel):
    poke_layout: PokeLayout


DEFAULT_USER_SETTINGS = UserSettingsRead(
    poke_layout=PokeLayout.LIST
)