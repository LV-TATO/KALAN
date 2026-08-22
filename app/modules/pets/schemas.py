from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Tamano = Literal["Pequeño", "Mediano", "Grande"]

class MascotaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    especie: str = Field(min_length=1, max_length=50)
    raza: str | None = None
    tamano: Tamano | None = None
    vacunas: bool = False
    castrada: bool = False
    zona: str | None = None
    descripcion: str = Field(min_length=1)
    foto_principal_url: str
    fotos_secundarias: list[str] = Field(default_factory=list, max_length=5)

class MascotaUpdate(BaseModel):
    nombre: str | None = None
    especie: str | None = None
    raza: str | None = None
    tamano: Tamano | None = None
    vacunas: bool | None = None
    castrada: bool | None = None
    zona: str | None = None
    descripcion: str | None = None
    foto_principal_url: str | None = None
    fotos_secundarias: list[str] | None = Field(default=None, max_length=5)

class MascotaOut(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    especie: str
    raza: str | None
    tamano: str | None
    vacunas: bool
    castrada: bool
    zona: str | None
    estado: str
    descripcion: str
    foto_principal_url: str
    fotos_secundarias: list[str]
    created_at: datetime