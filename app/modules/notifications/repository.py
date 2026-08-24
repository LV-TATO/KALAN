from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.notifications.models import Notificacion


class NotificationRepository(BaseRepository[Notificacion]):
    def __init__(self, db: Session):
        super().__init__(Notificacion, db)

    def get_by_usuario(self, usuario_id: int) -> list[Notificacion]:
        return (
            self.db.query(Notificacion)
            .filter(Notificacion.usuario_id == usuario_id)
            .order_by(Notificacion.created_at.desc())
            .all()
        )