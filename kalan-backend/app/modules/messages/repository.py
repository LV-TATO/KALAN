from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.messages.models import Conversacion, Mensaje


class ConversationRepository(BaseRepository[Conversacion]):
    def __init__(self, db: Session):
        super().__init__(Conversacion, db)

    def get_by_solicitud(self, solicitud_id: int) -> Conversacion | None:
        return self.db.query(Conversacion).filter(Conversacion.solicitud_id == solicitud_id).first()

    def get_by_avistamiento(self, avistamiento_id: int) -> Conversacion | None:
        return self.db.query(Conversacion).filter(Conversacion.avistamiento_id == avistamiento_id).first()


class MessageRepository(BaseRepository[Mensaje]):
    def __init__(self, db: Session):
        super().__init__(Mensaje, db)

    def get_by_conversacion(self, conversacion_id: int) -> list[Mensaje]:
        return (
            self.db.query(Mensaje)
            .filter(Mensaje.conversacion_id == conversacion_id)
            .order_by(Mensaje.created_at.asc())
            .all()
        )