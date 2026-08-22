from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException

class MascotaNoEncontradaException(NotFoundException):
    def __init__(self):
        super().__init__("Mascota no encontrada")

class NoEsPropietarioException(ForbiddenException):
    def __init__(self):
        super().__init__("No tienes permiso para modificar esta mascota")

class MascotaAdoptadaException(ConflictException):
    def __init__(self):
        super().__init__("No se puede modificar una mascota ya adoptada")