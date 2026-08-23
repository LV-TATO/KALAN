from fastapi import Depends, Query, WebSocket, WebSocketException, status as ws_status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.auth.exceptions import SesionInvalidaException
from app.modules.auth.models import Usuario
from app.modules.auth.repository import UsuarioRepository
from app.modules.auth.session_store import extend_session

from app.modules.auth.session_history_repository import SesionHistoryRepository

_bearer_scheme = HTTPBearer()

def _get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme)) -> dict:
    try:
        return decode_access_token(credentials.credentials)
    except JWTError:
        raise SesionInvalidaException()


def get_current_session_hash(
    payload: dict = Depends(_get_token_payload),
    db: Session = Depends(get_db),
) -> str:
    session_hash = payload.get("sid")
    if not session_hash or not extend_session(session_hash):
        if session_hash:
            SesionHistoryRepository(db).end(session_hash, "inactividad")
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

async def get_current_user_ws(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db),
) -> Usuario:
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise WebSocketException(code=ws_status.WS_1008_POLICY_VIOLATION)

    session_hash = payload.get("sid")
    user_id = payload.get("sub")
    if not session_hash or not user_id or not extend_session(session_hash):
        raise WebSocketException(code=ws_status.WS_1008_POLICY_VIOLATION)

    usuario = UsuarioRepository(db).get_by_id(int(user_id))
    if not usuario:
        raise WebSocketException(code=ws_status.WS_1008_POLICY_VIOLATION)

    return usuario