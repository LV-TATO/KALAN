from datetime import datetime

from sqlalchemy import ForeignKey, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Mensaje(Base):
    __tablename__ = "mensajes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), nullable=False)
    emisor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    receptor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())