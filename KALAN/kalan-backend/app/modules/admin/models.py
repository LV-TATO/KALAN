from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Reporte(Base):
    __tablename__ = "reportes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reportante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    mascota_id: Mapped[int | None] = mapped_column(ForeignKey("mascotas.id"), nullable=True)
    perdida_id: Mapped[int | None] = mapped_column(ForeignKey("perdidas.id"), nullable=True)
    avistamiento_id: Mapped[int | None] = mapped_column(ForeignKey("avistamientos.id"), nullable=True)
    motivo: Mapped[str] = mapped_column(String(30), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pendiente")
    admin_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    contenido_oculto: Mapped[bool] = mapped_column(Boolean, server_default="0", nullable=False)
    usuario_bloqueado: Mapped[bool] = mapped_column(Boolean, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.utc_timestamp())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)