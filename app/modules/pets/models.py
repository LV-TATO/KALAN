from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Mascota(Base):
    __tablename__="mascotas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    especie: Mapped[str] = mapped_column(String(50), nullable=False)
    raza: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tamano: Mapped[str | None] = mapped_column(String(20), nullable=True)
    vacunas: Mapped[bool] = mapped_column(Boolean, server_default="0", nullable=False)
    castrada: Mapped[bool] = mapped_column(Boolean, server_default="0", nullable=False)
    zona: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, server_default="activa")
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    foto_principal_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    fotos: Mapped[list["FotoMascota"]] = relationship(
        back_populates="mascota", cascade="all, delete-orphan"
    )

class FotoMascota(Base):
    __tablename__ = "fotos_mascota"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mascota_id: Mapped[int] = mapped_column(ForeignKey("mascotas.id"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)

    mascota: Mapped["Mascota"] = relationship(back_populates="fotos")