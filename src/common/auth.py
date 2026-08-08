from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, Query, Security, WebSocket, WebSocketException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from common.db import get_db
from common.exceptions import InvalidCredentialsError
from config import settings
from users.schemas import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/user/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def _resolve_user(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise InvalidCredentialsError("Could not validate credentials.") from exc

    user = db.get(User, user_id)
    if user is None:
        raise InvalidCredentialsError("Could not validate credentials.")
    return user


def get_current_user(
    token: str = Security(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolves the requesting user from a bearer JWT.

    Raises:
        InvalidCredentialsError: if the token is missing, invalid, expired, or its subject no longer exists.
    """
    return _resolve_user(token, db)


def get_current_user_ws(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolves the connecting user from a JWT passed as a `?token=` query param, since
    browsers can't set an Authorization header on the WebSocket handshake.

    Raises:
        WebSocketException: (close code 1008) if the token is missing, invalid, expired,
            or its subject no longer exists.
    """
    try:
        return _resolve_user(token, db)
    except InvalidCredentialsError as exc:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION) from exc
