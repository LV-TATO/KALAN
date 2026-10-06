from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Conversacion(Base):
    __tablename__ = "conversaciones"
    __table_args__ = (
        UniqueConstraint("solicitud_id"),
        UniqueConstraint("avistamiento_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    solicitud_id: Mapped[int | None] = mapped_column(ForeignKey("solicitudes.id"), nullable=True)
    avistamiento_id: Mapped[int | None] = mapped_column(ForeignKey("avistamientos.id"), nullable=True)
    participante_a_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    participante_b_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    mensajes: Mapped[list["Mensaje"]] = relationship(back_populates="conversacion", cascade="all, delete-orphan")


class Mensaje(Base):
    __tablename__ = "mensajes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversacion_id: Mapped[int] = mapped_column(ForeignKey("conversaciones.id"), nullable=False)
    emisor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    conversacion: Mapped["Conversacion"] = relationship(back_populates="mensajes")