from datetime import UTC, datetime, timedelta

import altcha

from common.exceptions import InvalidCaptchaError
from config import settings


def create_captcha_challenge() -> dict:
    """
    Builds a new ALTCHA (v1) proof-of-work challenge for the register/login widget to solve.

    Returns:
        dict: {algorithm, challenge, maxNumber, salt, signature}, as expected by the ALTCHA widget
    """
    challenge = altcha.create_challenge_v1(
        altcha.ChallengeOptionsV1(
            hmac_key=settings.ALTCHA_HMAC_KEY,
            max_number=settings.ALTCHA_MAX_NUMBER,
            expires=datetime.now(UTC)
            + timedelta(minutes=settings.ALTCHA_CHALLENGE_EXPIRE_MINUTES),
        )
    )
    return challenge.to_dict()


def verify_captcha(payload: str) -> None:
    """
    Verifies a base64-encoded ALTCHA solution payload against our HMAC key.

    Args:
        payload(str): the `altcha` value submitted by the widget

    Raises:
        InvalidCaptchaError: if the solution is missing, malformed, expired, or wrong
    """
    if not payload:
        raise InvalidCaptchaError("Missing captcha solution.")

    verified, error = altcha.verify_solution_v1(payload, settings.ALTCHA_HMAC_KEY)
    if not verified:
        raise InvalidCaptchaError(error or "Captcha verification failed.")
