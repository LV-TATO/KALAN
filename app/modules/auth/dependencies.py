from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.auth.exceptions import SesionInvalidaException
from app.modules.auth.models import Usuario
from app.modules.auth.repository import UsuarioRepository
from app.modules.auth.session_store import extend_session

_bearer_scheme = HTTPBearer()

def _get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme)) -> dict:
    try:
        return decode_access_token(credentials.credentials)
    except JWTError:
        raise SesionInvalidaException()


def get_current_session_hash(payload: dict = Depends(_get_token_payload)) -> str:
    session_hash = payload.get("sid")
    if not session_hash or not extend_session(session_hash):
        raise SesionInvalidaException()
    return session_hash


def get_current_user(
        session_hash: str = Depends(get_current_session_hash),
        payload: dict = Depends(_get_token_payload),
        db: Session = Depends(get_db),
) -> Usuario:
    user_id = payload.get("sub")
    if not user_id:
        raise SesionInvalidaException()

    usuario = UsuarioRepository(db).get_by_id(int(user_id))
    if not usuario:
        raise SesionInvalidaException()

    return usuario