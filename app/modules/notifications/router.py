from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.realtime import connection_manager
from app.modules.auth.dependencies import get_current_user, get_current_user_ws
from app.modules.auth.models import Usuario
from app.modules.notifications.schemas import NotificacionOut
from app.modules.notifications.service import CANAL_NOTIFICACIONES, NotificationService
from fastapi import WebSocket, WebSocketDisconnect

router = APIRouter()


@router.get("", response_model=list[NotificacionOut])
def list_notifications(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotificationService(db).get_list(usuario.id)


@router.patch("/{notificacion_id}/read", response_model=NotificacionOut)
def mark_read(notificacion_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotificationService(db).mark_read(notificacion_id, usuario.id)


@router.websocket("/ws")
async def notifications_websocket(websocket: WebSocket, usuario: Usuario = Depends(get_current_user_ws)):
    await connection_manager.connect(usuario.id, CANAL_NOTIFICACIONES, websocket)
    try:
        while True:
            await websocket.receive_text()  # no esperamos mensajes del cliente, solo mantenemos viva la conexión
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(usuario.id, CANAL_NOTIFICACIONES, websocket)