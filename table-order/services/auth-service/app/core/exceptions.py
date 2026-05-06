from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.error_code = code
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


class AuthenticationError(AppException):
    def __init__(self, code: str = "AUTH_002", message: str = "인증 정보가 올바르지 않습니다"):
        super().__init__(code=code, message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class AccountLockedError(AppException):
    def __init__(self, remaining_minutes: int = 15):
        super().__init__(
            code="AUTH_003",
            message=f"로그인 시도가 제한되었습니다. {remaining_minutes}분 후 다시 시도하세요",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class TokenExpiredError(AppException):
    def __init__(self):
        super().__init__(
            code="AUTH_004",
            message="세션이 만료되었습니다. 다시 로그인하세요",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenError(AppException):
    def __init__(self):
        super().__init__(
            code="AUTH_005",
            message="유효하지 않은 인증 정보입니다",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class StoreNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            code="AUTH_001",
            message="매장을 찾을 수 없습니다",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class TableNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            code="AUTH_006",
            message="테이블을 찾을 수 없습니다",
            status_code=status.HTTP_404_NOT_FOUND,
        )
