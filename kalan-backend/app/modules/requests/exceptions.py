from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException

class SolicitudNoEncontradaException(NotFoundException):
    def __init__(self):
        super().__init__("No se encontró la solicitud de adopción solicitada")

class MascotaNoDisponibleException(ConflictException):
    def __init__(self):
        super().__init__("La mascota no está disponible para recibir solicitudes de adopción")

class SolicitudPropiaException(ConflictException):
    def __init__(self):
        super().__init__("No puedes enviar una solicitud de adopción para una mascota publicada por ti")

class SolicitudDuplicadaExcepcion(ConflictException):
    def __init__(self):
        super().__init__("Ya tienes una solicitud de adopción pendiente para esta mascota")

class NoEsDuenoException(ForbiddenException):
    def __init__(self):
            super().__init__("No tienes permiso para aceptar o rechazar esta solicitud de adopción")

class SolicitudNoPendienteException(ConflictException):
    def __init__(self):
        super().__init__("Esta solicitud de adopción ya fue aceptada o rechazada")