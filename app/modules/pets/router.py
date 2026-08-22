from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.cloudinary_client import generate_upload_signature
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import Usuario
from app.modules.pets.models import Mascota
from app.modules.pets.schemas import MascotaCreate, MascotaOut, MascotaUpdate
from app.modules.pets.service import PetService

router = APIRouter()

def _to_out(mascota: Mascota) -> MascotaOut:
    return MascotaOut(
        id=mascota.id,
        usuario_id=mascota.usuario_id,
        nombre=mascota.nombre,
        especie=mascota.especie,
        raza=mascota.raza,
        tamano=mascota.tamano,
        vacunas=mascota.vacunas,
        castrada=mascota.castrada,
        zona=mascota.zona,
        estado=mascota.estado,
        descripcion=mascota.descripcion,
        foto_principal_url=mascota.foto_principal_url,
        fotos_secundarias=[foto.url for foto in mascota.fotos],
        created_at=mascota.created_at,
    )

@router.post("/upload-signature")
def get_upload_signature(usuario: Usuario = Depends(get_current_user)):
    return generate_upload_signature(folder="kalan/mascotas")

@router.get("", response_model=list[MascotaOut])
def list_pets(
    skip: int = 0, limit: int = 20,
    zona: str | None = None, raza: str | None = None,
    especie: str | None = None, tamano: str | None = None,
    db: Session = Depends(get_db),
):
    mascotas = PetService(db).list_pets(skip=skip, limit=limit, zona=zona, raza=raza, especie=especie, tamano=tamano)
    return [_to_out(m) for m in mascotas]

@router.get("/{mascota_id}", response_model=MascotaOut)
def get_pet(mascota_id: int, db: Session = Depends(get_db)):
    return _to_out(PetService(db).get_pet(mascota_id))

@router.post("", response_model=MascotaOut, status_code=status.HTTP_201_CREATED)
def create_pet(data: MascotaCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return _to_out(PetService(db).create_pet(data, usuario_id=usuario.id))

@router.put("/{mascota_id}", response_model=MascotaOut)
def update_pet(mascota_id: int, data: MascotaUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return _to_out(PetService(db).update_pet(mascota_id, data, usuario_id=usuario.id))

@router.delete("/{mascota_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(mascota_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    PetService(db).delete_pet(mascota_id, usuario_id=usuario.id)

@router.patch("/{mascota_id}/adot", response_model=MascotaOut)
def mark_adopted(mascota_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return _to_out(PetService(db).mark_adopted(mascota_id, usuario_id=usuario.id))