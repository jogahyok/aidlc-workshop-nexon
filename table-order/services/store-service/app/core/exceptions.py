from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.error_code = code
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


class StoreCodeDuplicateError(AppException):
    def __init__(self):
        super().__init__("STORE_001", "이미 존재하는 매장 코드입니다", status.HTTP_409_CONFLICT)


class TableNumberDuplicateError(AppException):
    def __init__(self):
        super().__init__("STORE_002", "이미 존재하는 테이블 번호입니다", status.HTTP_409_CONFLICT)


class ActiveSessionExistsError(AppException):
    def __init__(self):
        super().__init__("STORE_003", "활성 세션이 있는 테이블은 삭제할 수 없습니다", status.HTTP_409_CONFLICT)


class SessionAlreadyCompletedError(AppException):
    def __init__(self):
        super().__init__("STORE_004", "이미 종료된 세션입니다", status.HTTP_409_CONFLICT)


class OrderArchiveFailedError(AppException):
    def __init__(self):
        super().__init__("STORE_005", "주문 이력 처리 중 오류가 발생했습니다", status.HTTP_502_BAD_GATEWAY)
