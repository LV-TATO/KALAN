from sqlalchemy.orm import Session

from app.modules.lost.exceptions import CasoCerradoException, NoEsResponsableException, PerdidaNoEncontradaException
from app.modules.lost.models import Avistamiento, Perdida
from app.modules.lost.repository import LostRepository, SightingRepository
from app.modules.lost.schemas import AvistamientoCreate, PerdidaCreate

class LostService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = LostRepository(db)
        self.sighting_repository = SightingRepository(db)

    def list_lost(self, skip, limit, zona, especie) -> list[Perdida]:
        return self.repository.search(skip=skip, limit=limit, zona=zona, especie=especie)

    def get_lost(self, perdida_id: int) -> Perdida:
        perdida = self.repository.get_by_id(perdida_id)
        if not perdida:
            raise PerdidaNoEncontradaException()
        return perdida

    def create_lost(self, data: PerdidaCreate, usuario_id: int) -> Perdida:
        perdida = Perdida(usuario_id=usuario_id, **data.model_dump())
        return self.repository.create(perdida)

    def update_estado(self, perdida_id: int, nuevo_estado: str, usuario_id: int) -> Perdida:
        perdida = self.get_lost(perdida_id)
        if perdida.usuario_id != usuario_id:
            raise NoEsResponsableException()
        if perdida.estado == "Encontrada":
            raise CasoCerradoException()

        perdida.estado = nuevo_estado
        self.db.commit()
        self.db.refresh(perdida)
        # TODO (notifications): notificar al responsable cuando exista el módulo notifications
        return perdida

    def get_sightings(self, perdida_id: int) -> list[Avistamiento]:
        self.get_lost(perdida_id)
        return self.sighting_repository.get_by_perdida(perdida_id)

    def create_sighting(self, perdida_id: int, data: AvistamientoCreate, usuario_id: int) -> Avistamiento:
        perdida = self.get_lost(perdida_id)
        if perdida.estado == "Encontrada":
            raise CasoCerradoException()

        avistamiento = Avistamiento(perdida_id=perdida_id, usuario_id=usuario_id, **data.model_dump())
        self.sighting_repository.create(avistamiento)
        #TODO (notifications): notificar al responsable cuando exista el módulo notifications
        return avistamiento