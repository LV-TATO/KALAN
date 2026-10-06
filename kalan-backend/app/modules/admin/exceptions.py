from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException

class ReporteNoEncontradoException(NotFoundException):
    def __init__(self):
        super().__init__("Reporte no encontrado")

class UsuarioNoEncontradoException(NotFoundException):
    def __init__(self):
        super().__init__("Usuario no encontrado")

class ReporteDuplicadoException(ConflictException):
    def __init__(self):
        super().__init__("Ya tienes un reporte pendiente sonre este contenido")

class ObjetivoInvalidoExcepcion(ValidationException):
    def __init__(self):
        super().__init__("El objetivo del reporte no existe o no coincide con el tipo indicado")

class MotivoInvalidoException(ValidationException):
    def __init__(self):
        super().__init__("El contenido indicado no es valido para este tipo de contenido")

class ReporteYaResueltoException(ConflictException):
    def __init__(self):
        super().__init__("Este reporte ya fue resuelto")

class AccionNoPermitidaException(ForbiddenException):
    def __init__(self, detail: str):
        super().__init__(detail)