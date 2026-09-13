from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.admin.models import Reporte

class ReportRepository(BaseRepository[Reporte]):
    def __init__(self, db: Session):
        super().__init__(Reporte, db)

    def get_pendiente_duplicado(self, reportante_id: int, tipo: str, objetivo_id: int) -> Reporte | None:
        campo = f"{tipo}_id"
        return (
            self.db.query(Reporte)
            .filter(
                Reporte.reportante_id == reportante_id,
                Reporte.tipo == tipo,
                getattr(Reporte, campo) == objetivo_id,
                Reporte.estado == "pendiente",
            )
            .first()
        )

    def get_by_estado(self, estado: str | None) -> list[Reporte]:
        query = self.db.query(Reporte)
        if estado:
            query = query.filter(Reporte.estado == estado)
        return query.order_by(Reporte.created_at.desc()).all()