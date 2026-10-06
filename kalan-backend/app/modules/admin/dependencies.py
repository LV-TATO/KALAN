from fastapi import Depends

from app.common.exceptions import ForbiddenException
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import Usuario

def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.rol != "admin":
        raise ForbiddenException("Se requieren privilegios de administrador")
    return usuario