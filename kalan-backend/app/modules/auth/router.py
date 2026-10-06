from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_session_hash, get_current_user
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import (
    AccessTokenResponse, LoginRequest, RefreshRequest, TokenResponse,
    UsuarioCreate, UsuarioOut,
)
from app.modules.auth.service import AuthService

router = APIRouter()

_COOKIE_NAME = "refresh_token"
_COOKIE_MAX_AGE = settings.session_absolute_max_days * 24 * 60 * 60


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=_COOKIE_MAX_AGE,
        path="/api/v1/auth",
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UsuarioCreate, response: Response, db: Session = Depends(get_db)):
    tokens = AuthService(db).register(data)
    _set_refresh_cookie(response, tokens.refresh_token)
    return tokens


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    tokens = AuthService(db).login(data)
    _set_refresh_cookie(response, tokens.refresh_token)
    return tokens


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(request: Request, data: RefreshRequest | None = None, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get(_COOKIE_NAME) or (data.refresh_token if data else None)
    if not refresh_token:
        from app.modules.auth.exceptions import SesionInvalidaException
        raise SesionInvalidaException()
    return AuthService(db).refresh(refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, session_hash: str = Depends(get_current_session_hash), db: Session = Depends(get_db)):
    AuthService(db).logout_session(session_hash)
    response.delete_cookie(_COOKIE_NAME, path="/api/v1/auth")


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario