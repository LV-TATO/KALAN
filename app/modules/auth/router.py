from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_session_hash, get_current_user
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import (
    AccessTokenResponse, LoginRequest, RefreshRequest, TokenResponse,
    UsuarioCreate, UsuarioOut,
)
from app.modules.auth.service import AuthService

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UsuarioCreate, db: Session = Depends(get_db)):
    return AuthService(db).register(data)

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(data)

@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh(data.refresh_token)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(session_hash: str = Depends(get_current_session_hash), db: Session = Depends(get_db)):
    AuthService(db).logout_session(session_hash)

@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario