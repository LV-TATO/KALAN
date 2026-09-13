from datetime import datetime
from typing import Literal

from pydantic import BaseModel, model_validator

TipoReporte = Literal["mascota", "perdida", "avistamiento"]

MOTIVOS_PUBLICACION = {"informacion_falsa", "fraude", "contenido_inapropiado", "publicacion_duplicada", "imagen_no_correspondiente", "otro"}
MOTIVOS_AVISTAMIENTO = {"informacion_falsa", "ubicacion_sospechosa", "posible_engano", "acoso", "contenido_inapropiado", "otro"}

class ReporteCreate(BaseModel):
    tipo: TipoReporte
    mascota_id: int | None = None
    perdida_id: int | None = None
    avistamiento_id: int | None = None
    motivo: str
    descripcion: str | None = None

    @model_validator(mode="after")
    def validar_objetivo(self):
        objetivos = {"mascota": self.mascota_id, "perdida": self.perdida_id, "avistamiento": self.avistamiento_id}
        if objetivos[self.tipo] is None:
            raise ValueError(f"Debes inicr {self.tipo}_id para este tipo de reporte")
        if any(v is not None for k, v in objetivos.items() if k != self.tipo):
            raise ValueError("Solo debe de venir informado el campo correspondiente al tipo de reporte")
        return self

class ReporteResolucion(BaseModel):
    estado: Literal["resuelto", "descartado"]
    ocultar_contenido: bool = False
    bloquear_usuario: bool = False

    @model_validator(mode="after")
    def validar_coherencia(self):
        if self.estado == "descartado" and (self.ocultar_contenido or self.bloquear_usuario):
            raise ValueError("Un reporte descartado no puede combinarse con acciones de moderacion")
        return self

class ReporteOut(BaseModel):
    id: int
    reportante_id : int
    tipo: str
    mascota_id: int | None
    perdida_id: int | None
    avistamiento_id: int | None
    motivo: str
    descripcion: str | None
    estado: str
    admin_id: int | None
    contenido_oculto: bool
    usuario_bloqueado: bool
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}

class AdoptionStatsOut(BaseModel):
    mes: str
    zona: str | None
    especie: str
    total: int

