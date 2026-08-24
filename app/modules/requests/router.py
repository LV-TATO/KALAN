from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import Usuario
from app.modules.requests.schemas import SolicitudCreate, SolicitudDecision, SolicitudOut
from app.modules.requests.service import RequestService
from app.modules.messages.service import MessageService

router = APIRouter()

from app.modules.messages.service import MessageService


@router.post("", response_model=SolicitudOut, status_code=status.HTTP_201_CREATED)
def create_request(data: SolicitudCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    request_service = RequestService(db)
    solicitud = request_service.create_request(data, adoptante_id=usuario.id)
    try:
        MessageService(db).create_solicitud_conversation(solicitud)
    except Exception:
        request_service.repository.delete(solicitud)
        raise
    return solicitud

@router.get("/received", response_model=list[SolicitudOut])
def get_received(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return RequestService(db).get_received(dueno_id=usuario.id)

@router.get("/sent", response_model=list[SolicitudOut])
def get_sent(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return RequestService(db).get_sent(adoptante_id=usuario.id)

@router.patch("{solicitud_id}", response_model=SolicitudOut)
def decide_request(solicitud_id: int, data: SolicitudDecision, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return RequestService(db).decide(solicitud_id, data.estado, dueno_id=usuario.id)