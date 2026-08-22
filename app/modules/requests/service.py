from sqlalchemy.orm import Session

from app.modules.pets.repository import PetRepository
from app.modules.requests.exceptions import (
    MascotaNoDisponibleException, NoEsDuenoException, SolicitudDuplicadaExcepcion,
    SolicitudNoEncontradaException, SolicitudNoPendienteException, SolicitudPropiaException
)

from app.modules.requests.models import Solicitud
from app.modules.requests.repository import RequestRepository
from app.modules.requests.schemas import SolicitudCreate

class RequestService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = RequestRepository(db)
        self.pet_repository = PetRepository(db)

    def create_request(self, data: SolicitudCreate, adoptante_id: int) -> Solicitud:
        mascota = self.pet_repository.get_by_id(data.mascota_id)
        if not mascota or mascota.estado != "activa":
            raise MascotaNoDisponibleException()

        if mascota.usuario_id == adoptante_id:
            raise SolicitudPropiaException()

        if self.repository.get_pending_by_adoptante_and_mascota(adoptante_id, data.mascota_id):
            raise SolicitudDuplicadaExcepcion()

        solicitud = Solicitud(
            mascota_id=data.mascota_id,
            adoptante_id=adoptante_id,
            dueno_id=mascota.usuario_id,
        )
        return self.repository.create(solicitud)

    def get_received(self, dueno_id: int) -> list[Solicitud]:
        return self.repository.get_received(dueno_id)

    def get_sent(self, adoptante_id: int) -> list[Solicitud]:
        return self.repository.get_sent(adoptante_id)

    def decide(self, solicitud_id: int, nuevo_estado: str, dueno_id: int) -> Solicitud:
        solicitud = self.repository.get_by_id(solicitud_id)
        if not solicitud:
            raise SolicitudNoEncontradaException()
        if solicitud.dueno_id != dueno_id:
            raise NoEsDuenoException()
        if solicitud.estado != "pendiente":
            raise SolicitudNoPendienteException()

        solicitud.estado == nuevo_estado

        if nuevo_estado == "aceptada":
            mascota = self.pet_repository.get_by_id(solicitud.mascota_id)
            mascota.estado = "adoptada"
            for otra in self.repository.get_other_pending_for_mascota(solicitud.mascota_id, exclude_id=solicitud_id):
                otra.estado = "rechazada"

        self.db.commit()
        self.db.refresh(solicitud)
        return solicitud