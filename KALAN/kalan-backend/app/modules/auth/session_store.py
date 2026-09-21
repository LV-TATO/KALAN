import hashlib
import secrets
from datetime import datetime, timezone

from app.core.config import settings
from app.core.redis_client import redis_client

_SESSION_KEY_PREFIX = "sesion:"

def hash_token(token: str) -> str:
    """Convierte el refresh token en texto plano al valor que usamos como clave en Redis."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def _session_key(session_hash: str) -> str:
    return f"{_SESSION_KEY_PREFIX}{session_hash}"

def create_session(user_id: int) -> tuple[str, str]:
    """Genera un refresh token nuevo y su sesion en Redis,
    Devuelve (refresh_token, session_hash): el primero se entrega al cliente,
    el segundo es el que se guarda como cliente claim 'sid' del access token."""
    refresh_token = secrets.token_urlsafe(64)
    session_hash = hash_token(refresh_token)
    key = _session_key(session_hash)

    redis_client.hset(key, mapping={
        "user_id": str(user_id),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    redis_client.expire(key, settings.session_inactivity_minutes * 60)

    return refresh_token, session_hash

def extend_session(session_hash: str) -> bool:
    """Reinicia el TTl de inactividad, False si la sesion ya no existe(inactividad vencida o logout)."""
    key = _session_key(session_hash)
    return bool(redis_client.expire(key, settings.session_inactivity_minutes * 60))

def get_session(session_hash: str) -> dict | None:
    """Devuelve {'user_id': ..., 'created_at': ...} o None si la sesión no existe."""
    key = _session_key(session_hash)
    data = redis_client.hgetall(key)
    return data or None

def delete_session(session_hash:str) -> None:
    redis_client.delete(_session_key(session_hash))

def session_exists(session_hash: str) -> bool:
    """Verifica si la sesión sigue viva en Redis SIN renovar su TTL — a diferencia de extend_session."""
    return bool(redis_client.exists(_session_key(session_hash)))