from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    pass


class InvalidCredentialsError(CustomHTTPException):
    def __init__(self, desc: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=desc,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCaptchaError(CustomHTTPException):
    def __init__(self, desc: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=desc)
