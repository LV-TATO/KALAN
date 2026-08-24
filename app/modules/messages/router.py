from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, get_current_user_ws
from app.modules.auth.models import Usuario

from app.core.realtime import connection_manager
from app.modules.notifications.service import NotificationService

from app.modules.messages.models import Conversacion
from app.modules.messages.schemas import ConversacionOut, MensajeCreate, MensajeOut
from app.modules.messages.service import MessageService

router = APIRouter()


def _payload(mensaje) -> dict:
    return {
        "id": mensaje.id,
        "conversacion_id": mensaje.conversacion_id,
        "emisor_id": mensaje.emisor_id,
        "contenido": mensaje.contenido,
        "created_at": mensaje.created_at.isoformat(),
    }


async def _entregar_mensaje(
    db: Session,
    conversacion: Conversacion,
    receptor_id: int,
    emisor: Usuario,
    payload: dict,
):
    canal = f"conversacion:{conversacion.id}"

    if connection_manager.is_connected(receptor_id, canal):
        await connection_manager.send_to_channel(
            receptor_id,
            canal,
            payload,
        )
    else:
        await NotificationService(db).create(
            usuario_id=receptor_id,
            tipo="mensaje_nuevo",
            mensaje=f"Tienes un nuevo mensaje de {emisor.nombre}",
            conversacion_id=conversacion.id,
        )


@router.get(
    "/solicitud/{solicitud_id}",
    response_model=list[MensajeOut],
)
def get_solicitud_history(
    solicitud_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MessageService(db)
    conversacion = service.get_solicitud_conversation(
        solicitud_id,
        usuario.id,
    )
    return service.get_history(conversacion)


@router.post(
    "/solicitud/{solicitud_id}",
    response_model=MensajeOut,
    status_code=status.HTTP_201_CREATED,
)
async def send_solicitud_message(
    solicitud_id: int,
    data: MensajeCreate,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MessageService(db)

    conversacion = service.get_solicitud_conversation(
        solicitud_id,
        usuario.id,
    )

    mensaje = service.send_message(
        conversacion,
        data,
        emisor_id=usuario.id,
    )

    await _entregar_mensaje(
        db,
        conversacion,
        service.receptor_de(conversacion, usuario.id),
        usuario,
        _payload(mensaje),
    )

    return mensaje


@router.post(
    "/avistamiento/{avistamiento_id}/start",
    response_model=ConversacionOut,
    status_code=status.HTTP_201_CREATED,
)
def start_avistamiento_chat(
    avistamiento_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MessageService(db).start_avistamiento_conversation(
        avistamiento_id,
        usuario.id,
    )


@router.get(
    "/avistamiento/{avistamiento_id}",
    response_model=list[MensajeOut],
)
def get_avistamiento_history(
    avistamiento_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MessageService(db)

    conversacion = service.get_avistamiento_conversation(
        avistamiento_id,
        usuario.id,
    )

    return service.get_history(conversacion)


@router.post(
    "/avistamiento/{avistamiento_id}",
    response_model=MensajeOut,
    status_code=status.HTTP_201_CREATED,
)
async def send_avistamiento_message(
    avistamiento_id: int,
    data: MensajeCreate,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MessageService(db)

    conversacion = service.get_avistamiento_conversation(
        avistamiento_id,
        usuario.id,
    )

    mensaje = service.send_message(
        conversacion,
        data,
        emisor_id=usuario.id,
    )

    await _entregar_mensaje(
        db,
        conversacion,
        service.receptor_de(conversacion, usuario.id),
        usuario,
        _payload(mensaje),
    )

    return mensaje


async def _run_chat_socket(
    websocket: WebSocket,
    conversacion: Conversacion,
    usuario: Usuario,
    service: MessageService,
    db: Session,
):
    canal = f"conversacion:{conversacion.id}"

    await connection_manager.connect(
        usuario.id,
        canal,
        websocket,
    )

    try:
        while True:
            data = await websocket.receive_json()

            try:
                mensaje = service.send_message(
                    conversacion,
                    MensajeCreate(
                        contenido=data.get("contenido", "")
                    ),
                    emisor_id=usuario.id,
                )

            except Exception as e:
                await websocket.send_json(
                    {
                        "error": getattr(
                            e,
                            "detail",
                            "No se pudo enviar el mensaje",
                        )
                    }
                )
                continue

            payload = _payload(mensaje)

            await _entregar_mensaje(
                db,
                conversacion,
                service.receptor_de(
                    conversacion,
                    usuario.id,
                ),
                usuario,
                payload,
            )

            await websocket.send_json(payload)

    except WebSocketDisconnect:
        pass

    finally:
        connection_manager.disconnect(
            usuario.id,
            canal,
            websocket,
        )


@router.websocket("/ws/solicitud/{solicitud_id}")
async def solicitud_websocket(
    websocket: WebSocket,
    solicitud_id: int,
    usuario: Usuario = Depends(get_current_user_ws),
    db: Session = Depends(get_db),
):
    service = MessageService(db)

    try:
        conversacion = service.get_solicitud_conversation(
            solicitud_id,
            usuario.id,
        )

    except Exception:
        await websocket.close(code=1008)
        return

    await _run_chat_socket(
        websocket,
        conversacion,
        usuario,
        service,
        db,
    )


@router.websocket("/ws/avistamiento/{avistamiento_id}")
async def avistamiento_websocket(
    websocket: WebSocket,
    avistamiento_id: int,
    usuario: Usuario = Depends(get_current_user_ws),
    db: Session = Depends(get_db),
):
    service = MessageService(db)

    try:
        conversacion = service.get_avistamiento_conversation(
            avistamiento_id,
            usuario.id,
        )

    except Exception:
        await websocket.close(code=1008)
        return

    await _run_chat_socket(
        websocket,
        conversacion,
        usuario,
        service,
        db,
    )