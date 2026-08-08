from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from common.auth import get_current_user
from common.db import get_db
from config import settings
from push import service
from push.models import PushSubscriptionCreate, PushUnsubscribeRequest, VapidPublicKey
from users.schemas import User

push_router = APIRouter()


@push_router.get("/vapid-public-key")
def get_vapid_public_key() -> VapidPublicKey:
    """
    Returns the server's VAPID public key, used by the frontend as the
    `applicationServerKey` for `PushManager.subscribe()`.
    """
    return VapidPublicKey(public_key=settings.VAPID_PUBLIC_KEY)


@push_router.post("/subscribe")
def subscribe(
    subscription: PushSubscriptionCreate,
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Registers a browser push subscription for the current user, so pokes they
    receive can be delivered even when the app isn't open.

    Args:
        subscription(PushSubscriptionCreate): the PushSubscription from the browser's
            `PushManager.subscribe()`, as `{endpoint, keys: {p256dh, auth}}`
    """
    service.subscribe(db, current_user.id, subscription)


@push_router.post("/unsubscribe")
def unsubscribe(
    body: PushUnsubscribeRequest,
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Removes a previously registered push subscription for the current user.

    Args:
        body(PushUnsubscribeRequest): the subscription endpoint to remove
    """
    service.unsubscribe(db, current_user.id, body.endpoint)
