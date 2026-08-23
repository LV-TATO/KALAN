from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.auth.models import HistorialSesion

class SesionHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def start(self, usuario_id: int, session_hash:str) -> None:
        registro = HistorialSesion(usuario_id=usuario_id, session_hash=session_hash)
        self.db.add(registro)
        self.db.commit()

    def end(self, session_hash: str, reason: str) -> None:
        registro = (
            self.db.query(HistorialSesion)
            .filter(HistorialSesion.session_hash == session_hash, HistorialSesion.ended_at.is_(None))
            .order_by(HistorialSesion.started_at.desc())
            .first()
        )
        if registro:
            registro.ended_at = datetime.now(timezone.utc)
            registro.end_reason = reason
            self.db.commit()