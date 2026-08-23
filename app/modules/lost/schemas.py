from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

EstadoPerdida = Literal["Desaparecida", "Avistada", "Encontrada"]

class PerdidaCreate(BaseModel):
    mascota_id: int | None = None
    nombre: str = Field(min_length=1, max_length=100)
    especie: str = Field(min_length=1, max_length=50)
    raza: str | None = None
    descripcion: str | None = None
    foto_url: str
    zona: str | None = None
    ubicacion: str | None = None
    fecha_perdida: date

class PerdidaUpdate(BaseModel):
    estado: EstadoPerdida

class PerdidaOut(BaseModel):
    id: int
    mascota_id: int | None
    usuario_id: int
    nombre: str
    especie: str
    raza: str | None
    descripcion: str | None
    foto_url: str
    zona: str | None
    ubicacion: str | None
    fecha_perdida: date
    estado: str
    created_at: datetime

    model_config = {"from_attributes": True}

class AvistamientoCreate(BaseModel):
    foto_url: str | None = None
    descripcion: str | None = None

class AvistamientoOut(BaseModel):
    id: int
    perdida_id: int
    usuario_id: int
    foto_url: str | None
    descripcion: str | None
    created_at: datetime

    model_config = {"from_attributes": True}