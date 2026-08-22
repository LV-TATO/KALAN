from sqlalchemy.orm import Session

from app.modules.pets.exceptions import MascotaAdoptadaException, MascotaNoEncontradaException, NoEsPropietarioException
from app.modules.pets.models import FotoMascota, Mascota
from app.modules.pets.repository import PetRepository
from app.modules.pets.schemas import MascotaCreate, MascotaUpdate

class PetService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = PetRepository(db)

    def list_pets(self, skip, limit, zona, raza, especie, tamano) -> list[Mascota]:
        return self.repository.search(skip=skip, limit=limit, zona=zona, raza=raza, especie=especie, tamano=tamano)

    def get_pet(self, mascota_id: int) -> Mascota:
        mascota = self.repository.get_by_id(mascota_id)
        if not mascota:
            raise MascotaNoEncontradaException()
        return mascota

    def create_pet(self, data: MascotaCreate, usuario_id: int) -> Mascota:
        mascota = Mascota(
            usuario_id=usuario_id,
            nombre=data.nombre,
            especie=data.especie,
            raza=data.raza,
            tamano=data.tamano,
            vacunas=data.vacunas,
            castrada=data.castrada,
            zona=data.zona,
            descripcion=data.descripcion,
            foto_principal_url=data.foto_principal_url,
            fotos=[FotoMascota(url=url) for url in data.fotos_secundarias],
        )
        return self.repository.create(mascota)

    def update_pet(self, mascota_id: int, data: MascotaUpdate, usuario_id: int) -> Mascota:
        mascota = self.get_pet(mascota_id)
        self._verificar_propietario(mascota, usuario_id)
        if mascota.estado == "adoptada":
            raise MascotaAdoptadaException()

        cambios = data.model_dump(exclude_unset=True, exclude={"fotos_secundarias"})
        for campo, valor in cambios.items():
            setattr(mascota, campo, valor)

        if data.fotos_secundarias is not None:
            mascota.fotos = [FotoMascota(url=url) for url in data.fotos_secundarias]

        self.db.commit()
        self.db.refresh(mascota)
        return mascota

    def delete_pet(self, mascota_id: int, usuario_id: int) -> None:
        mascota = self.get_pet(mascota_id)
        self._verificar_propietario(mascota, usuario_id)
        if mascota.estado == "adoptada":
            raise MascotaAdoptadaException()
        self.repository.delete(mascota)

    def mark_adopted(self, mascota_id: int, usuario_id: int) -> Mascota:
        mascota = self.get_pet(mascota_id)
        self._verificar_propietario(mascota, usuario_id)
        if mascota.estado == "adoptada":
            raise MascotaAdoptadaException()
        mascota.estado = "adoptada"
        self.db.commit()
        self.db.refresh(mascota)
        return mascota

    def _verificar_propietario(self, mascota: Mascota, usuario_id: int) -> None:
        if mascota.usuario_id != usuario_id:
            raise NoEsPropietarioException()