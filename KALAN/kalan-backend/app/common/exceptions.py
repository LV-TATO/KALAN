class AppException(Exception):
    code: str = "ERROR"
    
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)

class NotFoundException(AppException):
    pass

class ConflictException(AppException):
    pass

class UnauthorizedException(AppException):
    pass

class ForbiddenException(AppException):
    pass

class ValidationException(AppException):
    pass