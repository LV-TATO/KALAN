from sqlalchemy.orm import Session

from app.modules.messages.exceptions import(
    ChatNoDisponibleException, NoParticipanteException, SolicitudInexistenteException,
)
from app.modules.messages.models import Mensaje
from app.modules.messages.repository import MessageRepository
from app.modules.messages.schemas import MensajeCreate
from app.modules.requests.repository import RequestRepository

class MessageService:
    def __init__(self, db: Session):
        self.repository = MessageRepository(db)
        self.request_repository = RequestRepository(db)

    def get_solicitud_valida(self, solicitud_id: int, usuaio_id: int):
        solicitud = self.request_repository.get_by_id(solicitud_id)
        if not solicitud:
            raise SolicitudInexistenteException()
        if usuaio_id not in (solicitud.dueno_id, solicitud.adoptante_id):
            raise NoParticipanteException()
        return solicitud

    def get_history(self, solicitud_id: int, usuario_id: int) -> list[Mensaje]:
        self.get_solicitud_valida(solicitud_id, usuario_id)
        return self.repository.get_by_solicitud(solicitud_id)

    def send_message(self, data: MensajeCreate, emisor_id: int) -> Mensaje:
        solicitud = self.get_solicitud_valida(data.solicitud_id, emisor_id)

        if solicitud.estado == "rechazada":
            raise ChatNoDisponibleException()

        receptor_id = solicitud.adoptante_id if emisor_id == solicitud.dueno_id else solicitud.dueno_id

        mensaje = Mensaje(
            solicitud_id=data.solicitud_id,
            emisor_id=emisor_id,
            receptor_id=receptor_id,
            contenido=data.contenido,
        )

        return self.repository.create(mensaje)