from datetime import datetime

from pydantic import BaseModel, Field

class MensajeCreate(BaseModel):
    solicitud_id: int
    contenido: str = Field(min_length=1)

class MensajeOut(BaseModel):
    id: int
    solicitud_id: int
    emisor_id: int
    receptor_id: int
    contenido: str
    created_at: datetime

    model_config = {"from_attributes": True}