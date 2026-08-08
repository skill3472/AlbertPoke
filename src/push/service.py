import json
import logging

from pywebpush import WebPushException, webpush
from requests import RequestException
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from push.models import PushSubscriptionCreate
from push.schemas import PushSubscription

logger = logging.getLogger(__name__)


def subscribe(db: Session, user_id: int, subscription: PushSubscriptionCreate) -> None:
    """
    Registers (or re-registers) a browser push subscription for a user.

    The same endpoint can end up re-subscribed by a different user on a shared
    device, so it's re-pointed at the current user rather than treated as a conflict.
    """
    stmt = select(PushSubscription).where(PushSubscription.endpoint == subscription.endpoint)
    existing = db.execute(stmt).scalar_one_or_none()

    if existing is not None:
        existing.user_id = user_id
        existing.p256dh = subscription.keys.p256dh
        existing.auth = subscription.keys.auth
    else:
        db.add(
            PushSubscription(
                user_id=user_id,
                endpoint=subscription.endpoint,
                p256dh=subscription.keys.p256dh,
                auth=subscription.keys.auth,
            )
        )
    db.commit()


def unsubscribe(db: Session, user_id: int, endpoint: str) -> None:
    stmt = select(PushSubscription).where(
        PushSubscription.user_id == user_id, PushSubscription.endpoint == endpoint
    )
    existing = db.execute(stmt).scalar_one_or_none()
    if existing is not None:
        db.delete(existing)
        db.commit()


def notify_user(db: Session, user_id: int, title: str, body: str) -> None:
    """
    Sends a Web Push notification to every device `user_id` has subscribed on.

    Best-effort: delivery failures are logged and never raised, and a subscription
    the push service reports as gone (404/410, e.g. the user uninstalled/reset
    permissions) is pruned. A poke must succeed regardless of whether push delivery
    does.
    """
    stmt = select(PushSubscription).where(PushSubscription.user_id == user_id)
    subscriptions = db.execute(stmt).scalars().all()

    payload = json.dumps({"title": title, "body": body})

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_SUBJECT},
            )
        except WebPushException as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code in (404, 410):
                db.delete(sub)
                db.commit()
            else:
                logger.warning("Push delivery failed for user %s: %s", user_id, exc)
        except RequestException as exc:
            logger.warning("Push delivery failed for user %s: %s", user_id, exc)
