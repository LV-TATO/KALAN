from sqlalchemy.orm import Session

from app.core.realtime import connection_manager
from app.modules.notifications.exceptions import NoEsDestinatarioException, NotificacionNoEncontradaException
from app.modules.notifications.models import Notificacion
from app.modules.notifications.repository import NotificationRepository

CANAL_NOTIFICACIONES = "notifications"


class NotificationService:
    def __init__(self, db: Session):
        self.repository = NotificationRepository(db)

    async def create(
        self, usuario_id: int, tipo: str, mensaje: str,
        solicitud_id: int | None = None, perdida_id: int | None = None, conversacion_id: int | None = None,
    ) -> Notificacion:
        notificacion = Notificacion(
            usuario_id=usuario_id, tipo=tipo, mensaje=mensaje,
            solicitud_id=solicitud_id, perdida_id=perdida_id, conversacion_id=conversacion_id,
        )
        self.repository.create(notificacion)

        if connection_manager.is_connected(usuario_id, CANAL_NOTIFICACIONES):
            await connection_manager.send_to_channel(usuario_id, CANAL_NOTIFICACIONES, {
                "id": notificacion.id,
                "tipo": notificacion.tipo,
                "mensaje": notificacion.mensaje,
                "solicitud_id": notificacion.solicitud_id,
                "perdida_id": notificacion.perdida_id,
                "conversacion_id": notificacion.conversacion_id,
                "created_at": notificacion.created_at.isoformat(),
            })
        return notificacion

    def get_list(self, usuario_id: int) -> list[Notificacion]:
        return self.repository.get_by_usuario(usuario_id)

    def mark_read(self, notificacion_id: int, usuario_id: int) -> Notificacion:
        notificacion = self.repository.get_by_id(notificacion_id)
        if not notificacion:
            raise NotificacionNoEncontradaException()
        if notificacion.usuario_id != usuario_id:
            raise NoEsDestinatarioException()
        notificacion.leida = True
        self.repository.db.commit()
        self.repository.db.refresh(notificacion)
        return notificacion