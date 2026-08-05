from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from common.auth import create_access_token, hash_password, verify_password
from common.captcha import create_captcha_challenge, verify_captcha
from common.db import get_db
from common.exceptions import InvalidCredentialsError
from users.exceptions import UserAlreadyExistsError, UserNotFoundError
from users.models import Token, UserCreate, UserRead
from users.schemas import User

users_router = APIRouter()


@users_router.get("/captcha")
def get_captcha_challenge() -> dict:
    """
    Issues a fresh ALTCHA proof-of-work challenge.

    Returns:
        dict: the challenge for the register/login widget to solve and submit back as `altcha`
    """
    return create_captcha_challenge()


@users_router.get("/search")
def search_users(query: str, db: Session = Depends(get_db)) -> list[UserRead]:
    """
    Search for users based on their name.

    Args:
        query(str): A string to search for users by.

    Returns:
        list[UserRead]: A list of found user's models

    Notes:
        - Query is case insensitive and can be a substring.
    """
    stmt = select(User).where(User.name.ilike(f"%{query}%"))
    users = db.execute(stmt).scalars().all()
    return [UserRead.model_validate(u) for u in users]


@users_router.post("/register")
def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """
    Registers a new user with a name and password.

    Args:
        user_in(UserCreate): the name, plaintext password, and solved captcha to register with

    Returns:
        UserRead: The newly created user model
    """
    verify_captcha(user_in.altcha)

    existing = db.execute(select(User).where(User.name == user_in.name)).scalar_one_or_none()
    if existing is not None:
        raise UserAlreadyExistsError(f"User with name '{user_in.name}' already exists.")

    user = User(name=user_in.name, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@users_router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    altcha: str = Form(...),
    db: Session = Depends(get_db),
) -> Token:
    """
    Exchanges a name + password + solved captcha for a bearer access token.

    Args:
        form_data(OAuth2PasswordRequestForm): standard OAuth2 form; `username` holds the user's name
        altcha(str): the solved captcha payload, submitted as an extra form field

    Returns:
        Token: a bearer access token to use for authenticated endpoints
    """
    verify_captcha(altcha)

    user = db.execute(select(User).where(User.name == form_data.username)).scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise InvalidCredentialsError("Incorrect name or password.")

    return Token(access_token=create_access_token(user.id))


@users_router.get("/get/{id}")
def get_user(id: int, db: Session = Depends(get_db)) -> UserRead:
    """
    Gets user by id.

    Args:
        id(int): user.id to search by

    Returns:
        UserRead: The found user model
    """
    user = db.get(User, id)
    if not user:
        raise UserNotFoundError(f"User with id: {id} was not found.")
    return UserRead.model_validate(user)
