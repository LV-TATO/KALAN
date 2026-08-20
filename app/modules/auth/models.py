from datetime import datetime

from sqlalchemy import String, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    zona: Mapped[str | None] = mapped_column(String(50), nullable=True)
    foto_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, server_default="user")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())