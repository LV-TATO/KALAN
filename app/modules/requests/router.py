from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import Usuario
from app.modules.auth.repository import UsuarioRepository
from app.modules.messages.service import MessageService
from app.modules.notifications.service import NotificationService
from app.modules.requests.models import Solicitud
from app.modules.requests.schemas import SolicitudCreate, SolicitudDecision, SolicitudOut
from app.modules.requests.service import RequestService

router = APIRouter()

def _to_out(solicitud: Solicitud, adoptante_nombre: str, dueno_nombre: str) -> SolicitudOut:
    return SolicitudOut(
        id=solicitud.id, mascota_id=solicitud.mascota_id,
        adoptante_id=solicitud.adoptante_id, dueno_id=solicitud.dueno_id,
        estado=solicitud.estado, created_at=solicitud.created_at,
        adoptante_nombre=adoptante_nombre, dueno_nombre=dueno_nombre,
    )

def _to_out_list(solicitudes: list[Solicitud], db: Session) -> list[SolicitudOut]:
    ids = {s.adoptante_id for s in solicitudes} | {s.dueno_id for s in solicitudes}
    nombres = UsuarioRepository(db).get_names_by_ids(list(ids))
    return [_to_out(s, nombres.get(s.adoptante_id, ""), nombres.get(s.dueno_id, "")) for s in solicitudes]

@router.post("", response_model=SolicitudOut, status_code=status.HTTP_201_CREATED)
async def create_request(data: SolicitudCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    request_service = RequestService(db)
    solicitud = request_service.create_request(data, adoptante_id=usuario.id)
    try:
        MessageService(db).create_solicitud_conversation(solicitud)
    except Exception:
        request_service.repository.delete(solicitud)
        raise

    dueno = UsuarioRepository(db).get_by_id(solicitud.dueno_id)
    await NotificationService(db).create(
        usuario_id=solicitud.dueno_id, tipo="solicitud_recibida",
        mensaje=f"{usuario.nombre} envio una solicitud de adopcion",
        solicitud_id=solicitud.id
    )
    return _to_out(solicitud, usuario.nombre, dueno.nombre if dueno else "")

@router.get("/received", response_model=list[SolicitudOut])
def get_received(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    solicitudes = RequestService(db).get_received(dueno_id=usuario.id)
    return _to_out_list(solicitudes, db)

@router.get("/sent", response_model=list[SolicitudOut])
def get_sent(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    solicitudes = RequestService(db).get_sent(adoptante_id=usuario.id)
    return _to_out_list(solicitudes, db)

@router.patch("/{solicitud_id}", response_model=SolicitudOut)
async def decide_request(solicitud_id: int, data: SolicitudDecision, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    solicitud = RequestService(db).decide(solicitud_id, data.estado, dueno_id=usuario.id)
    tipo = "solicitud_aceptada" if data.estado == "aceptada" else "solicitud_rechazada"
    await NotificationService(db).create(
        usuario_id=solicitud.adoptante_id, tipo=tipo,
        mensaje=f"Tu solicitud fue {data.estado}",
        solicitud_id=solicitud.id,
    )
    adoptante = UsuarioRepository(db).get_by_id(solicitud.adoptante_id)
    return _to_out(solicitud, adoptante.nombre if adoptante else "", usuario.nombre)