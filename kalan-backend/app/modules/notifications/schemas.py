from datetime import datetime

from pydantic import BaseModel


class NotificacionOut(BaseModel):
    id: int
    tipo: str
    mensaje: str
    leida: bool
    solicitud_id: int | None
    perdida_id: int | None
    conversacion_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}