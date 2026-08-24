from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException


class ConversacionNoEncontradaException(NotFoundException):
    def __init__(self):
        super().__init__("Conversación no encontrada")


class NoParticipanteException(ForbiddenException):
    def __init__(self):
        super().__init__("No tienes acceso a esta conversación")


class ChatNoDisponibleException(ConflictException):
    def __init__(self):
        super().__init__("Esta conversación ya no acepta nuevos mensajes")


class AvistamientoInexistenteException(NotFoundException):
    def __init__(self):
        super().__init__("El avistamiento no existe")


class NoEsResponsableDelReporteException(ForbiddenException):
    def __init__(self):
        super().__init__("Solo el responsable del reporte puede iniciar esta conversación")