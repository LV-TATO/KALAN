import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.dependencies import require_admin
from app.modules.admin.schemas import ReporteCreate, ReporteOut, ReporteResolucion
from app.modules.admin.service import AdminService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import Usuario
from app.modules.pets.models import Mascota
from app.modules.requests.models import Solicitud

router = APIRouter()

def _stats_query(db: Session):
    return (
        db.query(
            func.date_format(Solicitud.created_at, "%Y-%m").label("mes"),
            Mascota.zona, Mascota.especie, func.count(Solicitud.id).label("total"),
        )
        .join(Mascota, Mascota.id == Solicitud.mascota_id)
        .filter(Solicitud.estado == "aceptada")
        .group_by("mes", Mascota.zona, Mascota.especie)
        .all()
    )

@router.post("/reports", response_model=ReporteOut, status_code=201)
def create_report(data: ReporteCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return AdminService(db).create_report(data, reportante_id=usuario.id)

@router.get("/reports", response_model=list[ReporteOut])
def list_reports(estado: str | None = None, _: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    return AdminService(db).list_reports(estado)

@router.patch("/reports/{reporte_id}", response_model=ReporteOut)
async def resolve_report(reporte_id: int, data: ReporteResolucion, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    return await AdminService(db).resolve_report(reporte_id, data, admin_id=admin.id)

@router.patch("/users/{user_id}/block", status_code=204)
async def block_user(user_id: int, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    await AdminService(db).block_user(user_id, admin)

@router.patch("/users/{user_id}/unblock", status_code=204)
def unblock_user(user_id: int, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    AdminService(db).unblock_user(user_id, admin_id=admin.id)

@router.get("/stats/adoptions")
def adoption_stats(_: Usuario = Depends(require_admin), db : Session = Depends(get_db)):
    return [{"mes": r.mes, "zona": r.zona, "especie": r.especie, "total": r.total} for r in _stats_query(db)]

@router.get("/stats/export")
def export_stats(_: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["mes", "zona", "especie", "total"])
    for r in _stats_query(db):
        writer.writerow([r.mes, r.zona, r.especie, r.total])
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="text/csv", headers={"Content'Disposition": "attachment; filename=adopciones.csv"})