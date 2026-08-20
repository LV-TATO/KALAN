from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.auth.models import Usuario


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, db: Session):
        super().__init__(Usuario, db)

    def get_by_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()