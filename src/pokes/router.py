from fastapi import APIRouter, Depends, Security, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from common.auth import get_current_user, get_current_user_ws
from common.db import get_db
from pokes.models import PokeResponse, PokeStatus, PokeThread
from pokes.service import PokeService
from pokes.ws_manager import poke_connections
from users.schemas import User

pokes_router = APIRouter()


@pokes_router.websocket("/ws")
async def poke_websocket(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user_ws),
) -> None:
    """
    Live feed of pokes received by the current user, so the frontend can flip a
    friend's poke button back to "ready" the instant they poke, without a refresh.

    Auth is a `?token=` query param (a bearer JWT, same as the REST API) since the
    browser WebSocket API can't set an Authorization header. Sends one JSON message
    per poke received: `{"type": "poke", "from_user_id", "from_user_name", "streak"}`.
    The connection is otherwise passive - the server never expects incoming messages.
    """
    await poke_connections.connect(current_user.id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        poke_connections.disconnect(current_user.id, websocket)


@pokes_router.get("/threads")
def list_poke_threads(
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> list[PokeThread]:
    """
    Lists every user the current user has an ongoing poke thread with.

    Returns:
        list[PokeThread]: the other user, the pair's streak, whether the current user
            can poke now, and whether the current user sent the most recent poke
    """
    service = PokeService(db, current_user.id)
    return service.list_threads()


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
