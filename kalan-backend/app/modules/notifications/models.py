from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    leida: Mapped[bool] = mapped_column(Boolean, server_default="0", nullable=False)
    solicitud_id: Mapped[int | None] = mapped_column(ForeignKey("solicitudes.id"), nullable=True)
    perdida_id: Mapped[int | None] = mapped_column(ForeignKey("perdidas.id"), nullable=True)
    conversacion_id: Mapped[int | None] = mapped_column(ForeignKey("conversaciones.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())