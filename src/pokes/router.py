from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from common.auth import get_current_user
from common.db import get_db
from pokes.models import PokeResponse, PokeStatus
from pokes.service import PokeService
from users.schemas import User

pokes_router = APIRouter()


@pokes_router.get("/check")
def check_poke(
    target_user_id: int,
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> PokeStatus:
    """
    Checks whether the current user can poke `target_user_id` right now, and their streak.

    Args:
        target_user_id(int): id of the user to check poke status against

    Returns:
        PokeStatus: whether a poke can be sent right now, and the pair's total poke count
    """
    service = PokeService(db, current_user.id)
    return service.get_status(target_user_id)


@pokes_router.post("/poke")
def send_poke(
    poked_user_id: int,
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> PokeResponse:
    """
    Pokes `poked_user_id`, if it's the current user's turn and the rate limit has elapsed.

    Args:
        poked_user_id(int): id of the user to poke

    Returns:
        PokeResponse: the poked user's id, success flag, and the pair's new streak
    """
    service = PokeService(db, current_user.id)
    return service.poke(poked_user_id)
