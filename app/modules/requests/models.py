from datetime import datetime

from sqlalchemy import ForeignKey, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mascota_id: Mapped[int] = mapped_column(ForeignKey("mascotas.id"), nullable=False)
    adoptante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    dueno_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pendiente")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())