from app.common.exceptions import ConflictException, UnauthorizedException

class EmailYaRegistradoException(ConflictException):
    def __init__(self):
        super().__init__("El correo electrónico ya está registrado")


class CredencialesInvalidasException(UnauthorizedException):
    def __init__(self):
        super().__init__("El correo electrónico o la contraseña son incorrectos")


class SesionInvalidaException(UnauthorizedException):
    code = "SESSION_INVALID"
    def __init__(self):
        super().__init__("La sesión no es válida o ha vencido. Inicia sesión nuevamente")


class SesionExpiradaException(UnauthorizedException):
    code = "SESSION_INVALID"
    def __init__(self):
        super().__init__("La sesión alcanzó su duración máxima permitida. Inicia sesión nuevamente")

class UsuarioBloqueadoException(UnauthorizedException):
    code = "USER_BLOCKED"
    def __init__(self):
        super().__init__("Esta cuenta ha sido bloqueada")