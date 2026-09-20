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
from app.modules.auth.repository import UsuarioRepository
from app.modules.pets.models import Mascota
from app.modules.requests.models import Solicitud

router = APIRouter()

def _to_out(reporte, autor_id: int, nombres: dict[int, str]) -> ReporteOut:
    return ReporteOut(
        id=reporte.id, reportante_id=reporte.reportante_id,
        reportante_nombre=nombres.get(reporte.reportante_id, ""),
        tipo=reporte.tipo, mascota_id=reporte.mascota_id, perdida_id=reporte.perdida_id,
        avistamiento_id=reporte.avistamiento_id,
        usuario_reportado_id=autor_id,
        usuario_reportado_nombre=nombres.get(autor_id, ""),
        motivo=reporte.motivo, descripcion=reporte.descripcion, estado=reporte.estado,
        admin_id=reporte.admin_id, contenido_oculto=reporte.contenido_oculto,
        usuario_bloqueado=reporte.usuario_bloqueado, created_at=reporte.created_at,
        resolved_at=reporte.resolved_at,
    )

@router.post("/reports", response_model=ReporteOut, status_code=201)
def create_report(data: ReporteCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    reporte = service.create_report(data, reportante_id=usuario.id)
    autor_id = service.autor_de(reporte)
    nombres = UsuarioRepository(db).get_names_by_ids([reporte.reportante_id, autor_id])
    return _to_out(reporte, autor_id, nombres)

@router.get("/reports", response_model=list[ReporteOut])
def list_reports(estado: str | None = None, _: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    service = AdminService(db)
    reportes = service.list_reports(estado)
    autores = {r.id: service.autor_de(r) for r in reportes}
    ids = set(autores.values()) | {r.reportante_id for r in reportes}
    nombres = UsuarioRepository(db).get_names_by_ids(list(ids))
    return [_to_out(r, autores[r.id], nombres) for r in reportes]

@router.patch("/reports/{reporte_id}", response_model=ReporteOut)
async def resolve_report(reporte_id: int, data: ReporteResolucion, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    service = AdminService(db)
    reporte = await service.resolve_report(reporte_id, data, admin_id=admin.id)
    autor_id = service.autor_de(reporte)
    nombres = UsuarioRepository(db).get_names_by_ids([reporte.reportante_id, autor_id])
    return _to_out(reporte, autor_id, nombres)

@router.patch("/users/{user_id}/block", status_code=204)
async def block_user(user_id: int, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    await AdminService(db).block_user(user_id, admin)

@router.patch("/users/{user_id}/unblock", status_code=204)
def unblock_user(user_id: int, admin: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    AdminService(db).unblock_user(user_id, admin_id=admin.id)

@router.get("/stats/adoptions")
def adoption_stats(_: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    resultados = (
        db.query(
            func.date_format(Solicitud.created_at, "%Y-%m").label("mes"),
            Mascota.zona, Mascota.especie, func.count(Solicitud.id).label("total"),
        )
        .join(Mascota, Mascota.id == Solicitud.mascota_id)
        .filter(Solicitud.estado == "aceptada")
        .group_by("mes", Mascota.zona, Mascota.especie)
        .all()
    )
    return [{"mes": r.mes, "zona": r.zona, "especie": r.especie, "total": r.total} for r in resultados]

@router.get("/stats/export")
def export_stats(_: Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    resultados = (
        db.query(
            func.date_format(Solicitud.created_at, "%Y-%m").label("mes"),
            Mascota.zona, Mascota.especie, func.count(Solicitud.id).label("total"),
        )
        .join(Mascota, Mascota.id == Solicitud.mascota_id)
        .filter(Solicitud.estado == "aceptada")
        .group_by("mes", Mascota.zona, Mascota.especie)
        .all()
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["mes", "zona", "especie", "total"])
    for r in resultados:
        writer.writerow([r.mes, r.zona, r.especie, r.total])
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="text/csv", headers={"Content-Disposition": "attachment; filename.csv"})