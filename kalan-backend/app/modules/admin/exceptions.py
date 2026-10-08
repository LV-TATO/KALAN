from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException

class ReporteNoEncontradoException(NotFoundException):
    def __init__(self):
        super().__init__("No se encontró el reporte de moderación solicitado")

class UsuarioNoEncontradoException(NotFoundException):
    def __init__(self):
        super().__init__("No se encontró la cuenta de usuario solicitada")

class ReporteDuplicadoException(ConflictException):
    def __init__(self):
        super().__init__("Ya tienes un reporte de moderación pendiente sobre este contenido")

class ObjetivoInvalidoExcepcion(ValidationException):
    def __init__(self):
        super().__init__("No se encontró el contenido que deseas reportar para el tipo indicado")

class MotivoInvalidoException(ValidationException):
    def __init__(self):
        super().__init__("El motivo indicado no es válido para este tipo de reporte")

class ReporteYaResueltoException(ConflictException):
    def __init__(self):
        super().__init__("Este reporte ya fue resuelto o descartado y no admite una nueva resolución")

class AccionNoPermitidaException(ForbiddenException):
    def __init__(self, detail: str):
        super().__init__(detail)