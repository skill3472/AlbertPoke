from fastapi import status

from common.exceptions import CustomHTTPException


class CannotPokeSelfError(CustomHTTPException):
    def __init__(self, desc: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=desc)


class PokeRateLimitedError(CustomHTTPException):
    def __init__(self, desc: str):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=desc)


class NotMutualFriendsError(CustomHTTPException):
    def __init__(self, desc: str):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=desc)
