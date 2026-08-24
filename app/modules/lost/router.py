from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.cloudinary_client import generate_upload_signature
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import Usuario
from app.modules.lost.schemas import (
    AvistamientoCreate,
    AvistamientoOut,
    PerdidaCreate,
    PerdidaOut,
    PerdidaUpdate,
)
from app.modules.lost.service import LostService
from app.modules.notifications.service import NotificationService


router = APIRouter()


@router.post("/upload-signature")
def get_upload_signature(
    usuario: Usuario = Depends(get_current_user),
):
    return generate_upload_signature(
        folder="kalan/perdidas"
    )


@router.get("", response_model=list[PerdidaOut])
def list_lost(
    skip: int = 0,
    limit: int = 20,
    zona: str | None = None,
    especie: str | None = None,
    db: Session = Depends(get_db),
):
    return LostService(db).list_lost(
        skip=skip,
        limit=limit,
        zona=zona,
        especie=especie,
    )


@router.get("/{perdida_id}", response_model=PerdidaOut)
def get_lost(
    perdida_id: int,
    db: Session = Depends(get_db),
):
    return LostService(db).get_lost(perdida_id)


@router.post(
    "",
    response_model=PerdidaOut,
    status_code=status.HTTP_201_CREATED,
)
def create_lost(
    data: PerdidaCreate,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return LostService(db).create_lost(
        data,
        usuario_id=usuario.id,
    )


@router.patch("/{perdida_id}", response_model=PerdidaOut)
def update_lost(
    perdida_id: int,
    data: PerdidaUpdate,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return LostService(db).update_estado(
        perdida_id,
        data.estado,
        usuario_id=usuario.id,
    )


@router.get(
    "/{perdida_id}/avistamientos",
    response_model=list[AvistamientoOut],
)
def get_sightings(
    perdida_id: int,
    db: Session = Depends(get_db),
):
    return LostService(db).get_sightings(perdida_id)


@router.post(
    "/{perdida_id}/avistamientos",
    response_model=AvistamientoOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_sighting(
    perdida_id: int,
    data: AvistamientoCreate,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LostService(db)

    perdida = service.get_lost(perdida_id)

    avistamiento = service.create_sighting(
        perdida_id,
        data,
        usuario_id=usuario.id,
    )

    await NotificationService(db).create(
        usuario_id=perdida.usuario_id,
        tipo="avistamiento_registrado",
        mensaje=f"{usuario.nombre} reportó un avistamiento de {perdida.nombre}",
        perdida_id=perdida.id,
    )

    return avistamiento