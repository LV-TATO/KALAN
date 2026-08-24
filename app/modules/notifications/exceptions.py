from app.common.exceptions import ForbiddenException, NotFoundException


class NotificacionNoEncontradaException(NotFoundException):
    def __init__(self):
        super().__init__("Notificación no encontrada")


class NoEsDestinatarioException(ForbiddenException):
    def __init__(self):
        super().__init__("No tienes permiso sobre esta notificación")