from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.messages.models import Mensaje

class MessageRepository(BaseRepository[Mensaje]):
    def __init__(self, db: Session):
        super().__init__(Mensaje, db)

    def get_by_solicitud(self, solicitud_id: int) -> list[Mensaje]:
        return(
            self.db.query(Mensaje)
            .filter(Mensaje.solicitud_id == solicitud_id)
            .order_by(Mensaje.created_at.asc())
            .all()
        )