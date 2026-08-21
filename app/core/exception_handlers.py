from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.common.exceptions import(
    AppException, ConflictException, ForbiddenException,
    NotFoundException, UnauthorizedException, ValidationException,
)

_STATUS_MAP = {
    NotFoundException: 404,
    ConflictException: 409,
    UnauthorizedException: 401,
    ForbiddenException: 403,
    ValidationException: 422,
}

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def hundle_app_exception(request: Request, exc: AppException):
        status_code = 400
        for exc_type, code in _STATUS_MAP.items():
            if isinstance(exc, exc_type):
                status_code = code
                break
        return JSONResponse(status_code=status_code, content={"detail": exc.detail})