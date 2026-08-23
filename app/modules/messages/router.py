from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, get_current_user_ws
from app.modules.auth.models import Usuario
from app.modules.messages.connection_manager import connection_manager
from app.modules.messages.schemas import MensajeCreate, MensajeOut
from app.modules.messages.service import MessageService

router = APIRouter()

def _payload(mensaje) -> dict:
    return {
        "id": mensaje.id,
        "solicitud_id": mensaje.solicitud_id,
        "emisor_id": mensaje.emisor_id,
        "contenido": mensaje.contenido,
        "created_at": mensaje.created_at.isoformat(),
    }

@router.get("/{solicitud_id}", response_model=list[MensajeOut])
def get_history(solicitud_id: int, usuaio: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return MessageService(db).get_history(solicitud_id, usuario_id=usuaio.id)

@router.post("", response_model=MensajeOut, status_code=status.HTTP_201_CREATED)
async def send_message_rest(data: MensajeCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    mensaje = MessageService(db).send_message(data, emisor_id=usuario.id)
    await connection_manager.send_to_user(mensaje.receptor_id, payload=(mensaje))
    return mensaje

@router.websocket("/ws/{solicitud_id}")
async def chat_websocket(
    websocket: WebSocket,
    solicitud_id: int,
    usuario: Usuario = Depends(get_current_user_ws),
    db: Session = Depends(get_db),
):
    service = MessageService(db)
    try:
        service.get_solicitud_valida(solicitud_id, usuario.id)
    except Exception:
        await websocket.close(code=1008)
        return

    await connection_manager.connect(usuario.id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                mensaje = service.send_message(
                    MensajeCreate(solicitud_id=solicitud_id, contenido=data.get("contenido", "")),
                    emisor_id=usuario.id,
                )
            except Exception as e:
                await websocket.send_json({"error": getattr(e, "detail", "No se pudo enviar el mensaje")})
                continue

            payload = _payload(mensaje)
            await connection_manager.send_to_user(mensaje.receptor_id, payload)
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(usuario.id, websocket)