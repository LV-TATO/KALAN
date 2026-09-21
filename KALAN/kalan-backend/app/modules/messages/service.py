from sqlalchemy.orm import Session

from app.modules.lost.repository import LostRepository, SightingRepository
from app.modules.messages.exceptions import (
    AvistamientoInexistenteException, ChatNoDisponibleException, ConversacionNoEncontradaException,
    NoEsResponsableDelReporteException, NoParticipanteException,
)
from app.modules.messages.models import Conversacion, Mensaje
from app.modules.messages.repository import ConversationRepository, MessageRepository
from app.modules.messages.schemas import MensajeCreate
from app.modules.requests.repository import RequestRepository


class MessageService:
    def __init__(self, db: Session):
        self.repository = MessageRepository(db)
        self.conversation_repository = ConversationRepository(db)
        self.request_repository = RequestRepository(db)
        self.sighting_repository = SightingRepository(db)
        self.lost_repository = LostRepository(db)

    #Conversación de solicitud

    def create_solicitud_conversation(self, solicitud) -> Conversacion:
        conversacion = Conversacion(
            tipo="solicitud",
            solicitud_id=solicitud.id,
            participante_a_id=solicitud.dueno_id,
            participante_b_id=solicitud.adoptante_id,
        )
        return self.conversation_repository.create(conversacion)

    def get_solicitud_conversation(self, solicitud_id: int, usuario_id: int) -> Conversacion:
        conversacion = self.conversation_repository.get_by_solicitud(solicitud_id)
        if not conversacion:
            raise ConversacionNoEncontradaException()
        self._verificar_participante(conversacion, usuario_id)
        return conversacion

    #Conversación de avistamiento

    def start_avistamiento_conversation(self, avistamiento_id: int, usuario_id: int) -> Conversacion:
        avistamiento = self.sighting_repository.get_by_id(avistamiento_id)
        if not avistamiento:
            raise AvistamientoInexistenteException()

        perdida = self.lost_repository.get_by_id(avistamiento.perdida_id)
        if perdida.usuario_id != usuario_id:
            raise NoEsResponsableDelReporteException()

        existente = self.conversation_repository.get_by_avistamiento(avistamiento_id)
        if existente:
            return existente

        conversacion = Conversacion(
            tipo="avistamiento",
            avistamiento_id=avistamiento_id,
            participante_a_id=perdida.usuario_id,
            participante_b_id=avistamiento.usuario_id,
        )
        return self.conversation_repository.create(conversacion)

    def get_avistamiento_conversation(self, avistamiento_id: int, usuario_id: int) -> Conversacion:
        conversacion = self.conversation_repository.get_by_avistamiento(avistamiento_id)
        if not conversacion:
            raise ConversacionNoEncontradaException()
        self._verificar_participante(conversacion, usuario_id)
        return conversacion

    #Mensajes (compartido por las dos)

    def get_history(self, conversacion: Conversacion) -> list[Mensaje]:
        return self.repository.get_by_conversacion(conversacion.id)

    def send_message(self, conversacion: Conversacion, data: MensajeCreate, emisor_id: int) -> Mensaje:
        self._verificar_participante(conversacion, emisor_id)

        if conversacion.tipo == "solicitud":
            solicitud = self.request_repository.get_by_id(conversacion.solicitud_id)
            if solicitud.estado == "rechazada":
                raise ChatNoDisponibleException()
        # las conversaciones de avistamiento no tienen restricción por estado del reporte:
        # siguen activas aunque la mascota pase a "Encontrada" (decisión ya confirmada)

        mensaje = Mensaje(conversacion_id=conversacion.id, emisor_id=emisor_id, contenido=data.contenido)
        return self.repository.create(mensaje)

    def receptor_de(self, conversacion: Conversacion, emisor_id: int) -> int:
        return (
            conversacion.participante_b_id
            if emisor_id == conversacion.participante_a_id
            else conversacion.participante_a_id
        )

    def _verificar_participante(self, conversacion: Conversacion, usuario_id: int) -> None:
        if usuario_id not in (conversacion.participante_a_id, conversacion.participante_b_id):
            raise NoParticipanteException()