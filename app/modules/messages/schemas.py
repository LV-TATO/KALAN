from datetime import datetime

from pydantic import BaseModel, Field


class MensajeCreate(BaseModel):
    contenido: str = Field(min_length=1)


class MensajeOut(BaseModel):
    id: int
    conversacion_id: int
    emisor_id: int
    contenido: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversacionOut(BaseModel):
    id: int
    tipo: str
    solicitud_id: int | None
    avistamiento_id: int | None
    participante_a_id: int
    participante_b_id: int
    created_at: datetime

    model_config = {"from_attributes": True}