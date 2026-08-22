from datetime import datetime
from typing import Literal

from pydantic import BaseModel

class SolicitudCreate(BaseModel):
    mascota_id: int

class SolicitudDecision(BaseModel):
    estado: Literal["aceptada", "rechazada"]

class SolicitudOut(BaseModel):
    id: int
    mascota_id: int
    adoptante_id: int
    dueno_id: int
    estado: str
    created_at: datetime

    model_config = {"from_attributes": True}