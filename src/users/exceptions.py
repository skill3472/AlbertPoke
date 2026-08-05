from fastapi import status

from common.exceptions import CustomHTTPException


class UserNotFoundError(CustomHTTPException):
    def __init__(self, desc: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=desc)


class UserAlreadyExistsError(CustomHTTPException):
    def __init__(self, desc: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=desc)
