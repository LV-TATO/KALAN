from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException

class PerdidaNoEncontradaException(NotFoundException):
    def __init__(self):
        super().__init__("Reporte de mascota perdida no encontrado")

class NoEsResponsableException(ForbiddenException):
    def __init__(self):
        super().__init__("No tienes permiso para gestionar este reporte")

class CasoCerradoException(ConflictException):
    def __init__(self):
        super().__init__("Este caso ya fue marcado como encontrado")