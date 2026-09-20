from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.cloudinary_client import generate_upload_signature
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, get_optional_user
from app.modules.auth.models import Usuario
from app.modules.auth.repository import UsuarioRepository
from app.modules.lost.models import Avistamiento, Perdida
from app.modules.lost.schemas import (
    AvistamientoCreate, AvistamientoOut, PerdidaCreate, PerdidaOut, PerdidaUpdate,
)
from app.modules.lost.service import LostService

router = APIRouter()


def _perdida_out(p: Perdida, usuario_nombre: str) -> PerdidaOut:
    return PerdidaOut(
        id=p.id, mascota_id=p.mascota_id, usuario_id=p.usuario_id, nombre=p.nombre,
        especie=p.especie, raza=p.raza, descripcion=p.descripcion, foto_url=p.foto_url,
        zona=p.zona, ubicacion=p.ubicacion, fecha_perdida=p.fecha_perdida, estado=p.estado,
        created_at=p.created_at, usuario_nombre=usuario_nombre,
    )


def _avistamiento_out(a: Avistamiento, usuario_nombre: str) -> AvistamientoOut:
    return AvistamientoOut(
        id=a.id, perdida_id=a.perdida_id, usuario_id=a.usuario_id, foto_url=a.foto_url,
        descripcion=a.descripcion, created_at=a.created_at, usuario_nombre=usuario_nombre,
    )


@router.post("/upload-signature")
def get_upload_signature(usuario: Usuario = Depends(get_current_user)):
    return generate_upload_signature(folder="kalan/perdidas")


@router.get("", response_model=list[PerdidaOut])
def list_lost(skip: int = 0, limit: int = 20, zona: str | None = None, especie: str | None = None, db: Session = Depends(get_db)):
    perdidas = LostService(db).list_lost(skip=skip, limit=limit, zona=zona, especie=especie)
    nombres = UsuarioRepository(db).get_names_by_ids([p.usuario_id for p in perdidas])
    return [_perdida_out(p, nombres.get(p.usuario_id, "")) for p in perdidas]


@router.get("/{perdida_id}", response_model=PerdidaOut)
def get_lost(perdida_id: int, usuario: Usuario | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    perdida = LostService(db).get_lost(perdida_id, usuario)
    responsable = UsuarioRepository(db).get_by_id(perdida.usuario_id)
    return _perdida_out(perdida, responsable.nombre if responsable else "")


@router.post("", response_model=PerdidaOut, status_code=status.HTTP_201_CREATED)
def create_lost(data: PerdidaCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    perdida = LostService(db).create_lost(data, usuario_id=usuario.id)
    return _perdida_out(perdida, usuario.nombre)


@router.patch("/{perdida_id}", response_model=PerdidaOut)
def update_lost(perdida_id: int, data: PerdidaUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    perdida = LostService(db).update_estado(perdida_id, data.estado, usuario_id=usuario.id)
    return _perdida_out(perdida, usuario.nombre)


@router.get("/{perdida_id}/avistamientos", response_model=list[AvistamientoOut])
def get_sightings(perdida_id: int, usuario: Usuario | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    es_admin = usuario is not None and usuario.rol == "admin"
    avistamientos = LostService(db).get_sightings(perdida_id, es_admin=es_admin)
    nombres = UsuarioRepository(db).get_names_by_ids([a.usuario_id for a in avistamientos])
    return [_avistamiento_out(a, nombres.get(a.usuario_id, "")) for a in avistamientos]


@router.post("/{perdida_id}/avistamientos", response_model=AvistamientoOut, status_code=status.HTTP_201_CREATED)
async def create_sighting(perdida_id: int, data: AvistamientoCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.modules.notifications.service import NotificationService

    service = LostService(db)
    perdida = service.get_lost(perdida_id)
    avistamiento = service.create_sighting(perdida_id, data, usuario_id=usuario.id)
    await NotificationService(db).create(
        usuario_id=perdida.usuario_id, tipo="avistamiento_registrado",
        mensaje=f"{usuario.nombre} reportó un avistamiento de {perdida.nombre}",
        perdida_id=perdida.id,
    )
    return _avistamiento_out(avistamiento, usuario.nombre)