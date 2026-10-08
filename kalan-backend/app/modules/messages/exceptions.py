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
        super().__init__("No se encontró el registro del avistamiento solicitado")


class NoEsResponsableDelReporteException(ForbiddenException):
    def __init__(self):
        super().__init__("Solo el usuario que publicó el reporte de pérdida puede iniciar esta conversación")