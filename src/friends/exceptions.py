from fastapi import status

from common.exceptions import CustomHTTPException


class CannotFriendSelfError(CustomHTTPException):
    def __init__(self, desc: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=desc)
