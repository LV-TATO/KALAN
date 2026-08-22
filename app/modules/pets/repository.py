from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.pets.models import FotoMascota, Mascota

class PetRepository(BaseRepository[Mascota]):
    def __init__(self, db: Session):
        super().__init__(Mascota, db)

    def search(
        self,
        skip: int = 0,
        limit: int = 20,
        zona: str | None = None,
        raza: str | None = None,
        especie: str | None = None,
        tamano: str | None = None,
        estado: str = "activa",
    ) -> list[Mascota]:
        query = self.db.query(Mascota).filter(Mascota.estado == estado)

        if zona:
            query = query.filter(Mascota.zona == zona)
        if raza:
            query = query.filter(Mascota.raza == raza)
        if especie:
            query = query.filter(Mascota.especie == especie)
        if tamano:
            query = query.filter(Mascota.tamano == tamano)

        return query.offset(skip).limit(limit).all()

    def count_fotos_secundarias(self, mascota_id: int) -> int:
        return self.db.query(FotoMascota).filter(FotoMascota.mascota_id == mascota_id).count()