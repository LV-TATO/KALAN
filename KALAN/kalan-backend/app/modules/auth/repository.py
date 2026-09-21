from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.auth.models import Usuario


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, db: Session):
        super().__init__(Usuario, db)

    def get_by_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def get_names_by_ids(self, ids: list[int]) -> dict[int, str]:
        if not ids:
            return {}
        filas = self.db.query(Usuario.id, Usuario.nombre).filter(Usuario.id.in_(set(ids))).all()
        return {id_: nombre for id_, nombre in filas}