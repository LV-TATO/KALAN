import asyncio
import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.realtime import connection_manager
from app.modules.auth.dependencies import get_current_user, get_current_user_ws, WSAuthContext
from app.modules.auth.models import Usuario
from app.modules.auth.session_store import session_exists
from app.modules.notifications.schemas import NotificacionOut
from app.modules.notifications.service import NotificationService, CANAL_NOTIFICACIONES

router = APIRouter()

@router.get("", response_model=list[NotificacionOut])
def list_notifications(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotificationService(db).get_list(usuario.id)

@router.patch("/{notificacion_id}/read", response_model=NotificacionOut)
def mark_read(notificacion_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotificationService(db).mark_read(notificacion_id, usuario.id)

@router.websocket("/ws")
async def notifications_websocket(websocket: WebSocket,
    ctx: WSAuthContext = Depends(get_current_user_ws),
    db: Session = Depends(get_db)):
    usuario = ctx.usuario
    await connection_manager.connect(usuario.id, CANAL_NOTIFICACIONES, websocket)
    try:
        while True:
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=60)
                try:
                    mensaje = json.loads(raw)
                except ValueError:
                    mensaje = {}
                if mensaje.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                pass

            if not session_exists(ctx.session_hash):
                await websocket.close(code=1008)
                return

            db.refresh(usuario)
            if usuario.bloqueado:
                await websocket.close(code=1008)
                return
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(usuario.id, CANAL_NOTIFICACIONES, websocket)