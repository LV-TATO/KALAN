from app.common.exceptions import ConflictException, UnauthorizedException

class EmailYaRegistradoException(ConflictException):
    def __init__(self):
        super().__init__("El email ya esta registrado")


class CredencialesInvalidasException(UnauthorizedException):
    def __init__(self):
        super().__init__("Credenciales invalidas")


class SesionInvalidaException(UnauthorizedException):
    code = "SESSION_INVALID"
    def __init__(self):
        super().__init__("Sesion invalida o expirada")


class SesionExpiradaException(UnauthorizedException):
    code = "SESSION_INVALID"
    def __init__(self):
        super().__init__("La sesion alcanzo su duracion maxima, inicia sesion de nuevo")

class UsuarioBloqueadoException(UnauthorizedException):
    code = "USER_BLOCKED"
    def __init__(self):
        super().__init__("Esta cuenta ha sido bloqueada")