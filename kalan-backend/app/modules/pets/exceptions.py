from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException

class MascotaNoEncontradaException(NotFoundException):
    def __init__(self):
        super().__init__("No se encontró el registro de la mascota solicitada")

class NoEsPropietarioException(ForbiddenException):
    def __init__(self):
        super().__init__("No tienes permiso para realizar esta operación sobre el registro de esta mascota")

class MascotaAdoptadaException(ConflictException):
    def __init__(self):
        super().__init__("No se puede modificar ni eliminar el registro de una mascota que ya figura como adoptada")