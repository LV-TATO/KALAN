from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, String, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Perdida(Base):
    __tablename__ = "perdidas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mascota_id: Mapped[int | None] = mapped_column(ForeignKey("mascotas.id"), nullable=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    especie: Mapped[str] = mapped_column(String(50), nullable=False)
    raza: Mapped[str | None] = mapped_column(String(100), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    foto_url: Mapped[str] = mapped_column(Text,nullable=False)
    zona: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ubicacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_perdida: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, server_default="Desaparecida")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    avistamientos: Mapped[list["Avistamiento"]] = relationship(
        back_populates="perdida", cascade="all, delete-orphan"
    )

class Avistamiento(Base):
    __tablename__ = "avistamientos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    perdida_id: Mapped[int] = mapped_column(ForeignKey("perdidas.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    foto_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    perdida: Mapped["Perdida"] = relationship(back_populates="avistamientos")