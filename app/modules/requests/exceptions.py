from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException

class SolicitudNoEncontradaException(NotFoundException):
    def __init__(self):
        super().__init__("Solicitud no encontrada")

class MascotaNoDisponibleException(ConflictException):
    def __init__(self):
        super().__init__("La mascota no esta disponible para adopcion")

class SolicitudPropiaException(ConflictException):
    def __init__(self):
        super().__init__("No puedes enviar una solicitud sobre tu propias mascota")

class SolicitudDuplicadaExcepcion(ConflictException):
    def __init__(self):
        super().__init__("Ya existe una solicitud pendiente para esta mascota")

class NoEsDuenoException(ForbiddenException):
    def __init__(self):
            super().__init__("No tienes permiso para gestionar esta solicitud")

class SolicitudNoPendienteException(ConflictException):
    def __init__(self):
        super().__init__("Esta solicitud ya fue procesada")