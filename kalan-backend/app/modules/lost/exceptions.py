from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException

class PerdidaNoEncontradaException(NotFoundException):
    def __init__(self):
        super().__init__("No se encontró el reporte de pérdida solicitado")

class NoEsResponsableException(ForbiddenException):
    def __init__(self):
        super().__init__("No tienes permiso para cambiar el estado de este reporte de pérdida")

class CasoCerradoException(ConflictException):
    def __init__(self):
        super().__init__("El reporte de pérdida está cerrado porque la mascota ya fue marcada como encontrada")