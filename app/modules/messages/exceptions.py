from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException

class SolicitudInexistenteException(NotFoundException):
    def __init__(self):
        super().__init__("La solicitud asociada no existe")

class NoParticipanteException(ForbiddenException):
    def __init__(self):
        super().__init__("No tienes acceso a esta conversacion")

class ChatNoDisponibleException(ConflictException):
    def __init__(self):
        super().__init__("Esta conversacion ya no acepta nuevos mensajes")