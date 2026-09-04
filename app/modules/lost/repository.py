from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.lost.models import Avistamiento, Perdida

class LostRepository(BaseRepository[Perdida]):
    def __init__(self, db: Session):
        super().__init__(Perdida, db)

    def search(self, skip=0, limit=20, zona=None, especie=None, estado_excluir="Encontrada"):
        query = self.db.query(Perdida)
        if estado_excluir:
            query = query.filter(Perdida.estado != estado_excluir)
        if zona:
            query = query.filter(Perdida.zona == zona)
        if especie:
            query = query.filter(Perdida.especie == especie)
        return query.order_by(Perdida.created_at.desc()).offset(skip).limit(limit).all()

class SightingRepository(BaseRepository[Avistamiento]):
    def __init__(self, db: Session):
        super().__init__(Avistamiento, db)

    def get_by_perdida(self, perdida_id: int) -> list[Avistamiento]:
        return (
            self.db.query(Avistamiento)
            .filter(Avistamiento.perdida_id == perdida_id)
            .order_by(Avistamiento.created_at.desc())
            .all()
        )