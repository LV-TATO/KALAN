from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.common.exceptions import ConflictException, UnauthorizedException
from app.core.config import settings
from app.core.security import create_acces_token, hash_password, verify_password
from app.modules.auth.models import Usuario
from app.modules.auth.repository import UsuarioRepository
from app.modules.auth.schemas import (
    AccessTokenResponse, LoginRequest, TokenResponse, UsuarioCreate
)
from app.modules.auth.session_store import (
    create_session, delete_session, extend_session, get_session, hash_token,
)

from app.modules.auth.exceptions import (
    CredencialesInvalidasException, EmailYaRegistradoException,
    SesionExpiradaException, SesionInvalidaException
)

from app.modules.auth.session_history_repository import SesionHistoryRepository

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UsuarioRepository(db)
        self.history_repository = SesionHistoryRepository(db)

    def register(self, data: UsuarioCreate) -> TokenResponse:
        if self.repository.get_by_email(data.email):
            raise EmailYaRegistradoException()

        usuario = Usuario(
            email=data.email,
            password_hash=hash_password(data.password),
            nombre=data.nombre,
            zona=data.zona,
        )
        self.repository.create(usuario)
        return self._issue_tokens(usuario.id)

    def login(self, data: LoginRequest) -> TokenResponse:
        usuario = self.repository.get_by_email(data.email)
        if not usuario or not verify_password(data.password, usuario.password_hash):
            raise CredencialesInvalidasException()
        return self._issue_tokens(usuario.id)

    def refresh(self, refresh_token: str) -> AccessTokenResponse:
        session_hash = hash_token(refresh_token)
        session = get_session(session_hash)
        if not session:
            self.history_repository.end(session_hash, "inactividad")
            raise SesionInvalidaException()

        created_at = datetime.fromisoformat(session["created_at"])
        max_age = timedelta(days=settings.session_absolute_max_days)
        if datetime.now(timezone.utc) - created_at > max_age:
            delete_session(session_hash)
            self.history_repository.end(session_hash, "limite_absoluto")
            raise SesionExpiradaException()

        extend_session(session_hash)
        access_token = create_acces_token({"sub": session["user_id"], "sid": session_hash})
        return AccessTokenResponse(access_token=access_token)

    def logout_session(self, session_hash: str) -> None:
        delete_session(session_hash)
        self.history_repository.end(session_hash, "logout")

    def _issue_tokens(self, user_id: int) -> TokenResponse:
        refresh_token, session_hash = create_session(user_id)
        self.history_repository.start(user_id, session_hash)
        access_token = create_acces_token({"sub": str(user_id), "sid": session_hash})
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)