from datetime import UTC, datetime, timedelta
from math import ceil

from anyio.from_thread import run as run_async_from_thread
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from config import settings
from friends.models import FriendBrief
from friends.service import are_mutual_friends
from pokes.exceptions import (
    CannotPokeSelfError,
    NotMutualFriendsError,
    PokeRateLimitedError,
)
from pokes.models import PokeResponse, PokeStatus, PokeThread
from pokes.schemas import Poke
from pokes.ws_manager import poke_connections
from push.service import notify_user
from users.exceptions import UserNotFoundError
from users.schemas import User


class PokeService:
    def __init__(self, db: Session, logged_in_user_id: int):
        self.db = db
        self.logged_in_user_id = logged_in_user_id
        self.logged_in_user = self._get_user(logged_in_user_id)

    def get_status(self, other_user_id: int) -> PokeStatus:
        """
        Checks whether the current user can poke `other_user_id` right now, and their streak.

        Args:
            other_user_id(int): id of the user to check poke status against

        Returns:
            PokeStatus: whether a poke can be sent right now, and the pair's total poke count
        """
        self._get_user(other_user_id)
        return PokeStatus(
            can_poke=self._can_poke(other_user_id),
            streak=self._streak(other_user_id),
            mutual=are_mutual_friends(self.db, self.logged_in_user_id, other_user_id),
            cooldown_seconds=self._cooldown_seconds(other_user_id),
        )

    def list_threads(self) -> list[PokeThread]:
        """
        Lists every user the current user has an ongoing poke thread with, i.e. has ever
        poked or been poked by.

        Returns:
            list[PokeThread]: the other user, the pair's streak, whether the current user
                can poke now, and whether the current user sent the most recent poke
        """
        stmt = select(Poke.from_user_id, Poke.to_user_id).where(
            or_(
                Poke.from_user_id == self.logged_in_user_id,
                Poke.to_user_id == self.logged_in_user_id,
            )
        )
        other_user_ids = {
            to_id if from_id == self.logged_in_user_id else from_id
            for from_id, to_id in self.db.execute(stmt).all()
        }

        threads = []
        for other_id in other_user_ids:
            other_user = self._get_user(other_id)
            last_poke = self._last_poke_between(other_id)
            threads.append(
                PokeThread(
                    user=FriendBrief.model_validate(other_user),
                    streak=self._streak(other_id),
                    can_poke=self._can_poke(other_id),
                    last_poke_mine=last_poke is not None
                    and last_poke.from_user_id == self.logged_in_user_id,
                    mutual=are_mutual_friends(self.db, self.logged_in_user_id, other_id),
                    cooldown_seconds=self._cooldown_seconds(other_id),
                )
            )
        return threads

    def poke(self, other_user_id: int) -> PokeResponse:
        """
        Sends a poke from the current user to `other_user_id`.

        Args:
            other_user_id(int): id of the user to poke

        Returns:
            PokeResponse: the poked user's id, success flag, and the pair's new streak

        Raises:
            CannotPokeSelfError: if the current user tries to poke themselves
            NotMutualFriendsError: if the two users are not mutual friends
            PokeRateLimitedError: if it isn't the current user's turn, or the rate limit hasn't elapsed
        """
        if other_user_id == self.logged_in_user_id:
            raise CannotPokeSelfError("You cannot poke yourself.")
        self._get_user(other_user_id)

        if not are_mutual_friends(self.db, self.logged_in_user_id, other_user_id):
            raise NotMutualFriendsError("You can only poke mutual friends.")

        if not self._can_poke(other_user_id):
            raise PokeRateLimitedError(
                "You must wait for a response, or for the rate limit to elapse, before poking again."
            )

        self.db.add(Poke(from_user_id=self.logged_in_user_id, to_user_id=other_user_id))
        self.db.commit()

        streak = self._streak(other_user_id)

        recipient_service = PokeService(self.db, other_user_id)
        recipient_can_poke = recipient_service._can_poke(self.logged_in_user_id)

        notify_user(
            self.db,
            other_user_id,
            title=f"{self.logged_in_user.name} poked you!",
            body=f"Streak: {streak}",
        )
        run_async_from_thread(
            poke_connections.send_to_user,
            other_user_id,
            {
                "type": "poke",
                "from_user_id": self.logged_in_user_id,
                "from_user_name": self.logged_in_user.name,
                "streak": streak,
                "can_poke": recipient_can_poke,
                "cooldown_seconds": recipient_service._cooldown_seconds(self.logged_in_user_id),
            },
        )

        return PokeResponse(
            user_id=other_user_id,
            success=True,
            current_streak=streak,
        )

    def _get_user(self, user_id: int) -> User:
        user = self.db.get(User, user_id)
        if user is None:
            raise UserNotFoundError(f"User with id: {user_id} was not found.")
        return user

    def _pair_filter(self, other_user_id: int):
        return or_(
            and_(Poke.from_user_id == self.logged_in_user_id, Poke.to_user_id == other_user_id),
            and_(Poke.from_user_id == other_user_id, Poke.to_user_id == self.logged_in_user_id),
        )

    def _last_poke_between(self, other_user_id: int) -> Poke | None:
        stmt = (
            select(Poke)
            .where(self._pair_filter(other_user_id))
            .order_by(Poke.timestamp.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def _last_own_poke(self, other_user_id: int) -> Poke | None:
        stmt = (
            select(Poke)
            .where(Poke.from_user_id == self.logged_in_user_id, Poke.to_user_id == other_user_id)
            .order_by(Poke.timestamp.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def _streak(self, other_user_id: int) -> int:
        """Total pokes sent between the pair, in either direction."""
        stmt = select(func.count()).select_from(Poke).where(self._pair_filter(other_user_id))
        return self.db.execute(stmt).scalar_one()

    def _can_poke(self, other_user_id: int) -> bool:
        if not are_mutual_friends(self.db, self.logged_in_user_id, other_user_id):
            return False

        last_poke = self._last_poke_between(other_user_id)
        if last_poke is None:
            return True

        if last_poke.from_user_id == self.logged_in_user_id:
            # We poked last; waiting on other_user_id to poke back.
            return False

        # other_user_id poked last, so it's our turn - but we still owe the rate
        # limit against our own last poke to them, even though they already responded.
        own_last_poke = self._last_own_poke(other_user_id)
        if own_last_poke is None:
            return True

        elapsed = datetime.now(UTC).replace(tzinfo=None) - own_last_poke.timestamp
        return elapsed >= timedelta(seconds=settings.POKE_RATE_LIMIT_SECONDS)

    def _cooldown_seconds(self, other_user_id: int) -> int:
        """
        Seconds left on our own rate limit against `other_user_id`, i.e. how long
        until we could poke again once they've responded. 0 if we have no poke
        history with them, or the rate limit has already elapsed.
        """
        own_last_poke = self._last_own_poke(other_user_id)
        if own_last_poke is None:
            return 0

        elapsed = datetime.now(UTC).replace(tzinfo=None) - own_last_poke.timestamp
        remaining = timedelta(seconds=settings.POKE_RATE_LIMIT_SECONDS) - elapsed
        return max(0, ceil(remaining.total_seconds()))
