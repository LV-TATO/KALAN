from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.requests.models import Solicitud

class RequestRepository(BaseRepository[Solicitud]):
    def __init__(self, db: Session):
        super().__init__(Solicitud, db)

    def get_pending_by_adoptante_and_mascota(self, adoptante_id: int, mascota_id: int) -> Solicitud | None:
        return (
            self.db.query(Solicitud)
            .filter(
                Solicitud.adoptante_id == adoptante_id,
                Solicitud.mascota_id == mascota_id,
                Solicitud.estado == "pendiente",
            )
            .first()
        )

    def get_received(self, dueno_id: int) -> list[Solicitud]:
        return self.db.query(Solicitud).filter(Solicitud.dueno_id == dueno_id).all()

    def get_sent(self, adoptante_id: int) -> list[Solicitud]:
        return self.db.query(Solicitud).filter(Solicitud.adoptante_id == adoptante_id).all()

    def get_other_pending_for_mascota(self, mascota_id: int, exclude_id: int) -> list[Solicitud]:
        return(
            self.db.query(Solicitud)
            .filter(
                Solicitud.mascota_id == mascota_id,
                Solicitud.estado == "pendiente",
                Solicitud.id != exclude_id,
            )
            .all()
        )