from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.admin.exceptions import(
    AccionNoPermitidaException, MotivoInvalidoException, ObjetivoInvalidoExcepcion,
    ReporteDuplicadoException, ReporteNoEncontradoException, ReporteYaResueltoException,
    UsuarioNoEncontradoException
)
from app.modules.admin.models import Reporte
from app.modules.admin.repository import ReportRepository
from app.modules.admin.schemas import MOTIVOS_AVISTAMIENTO, MOTIVOS_PUBLICACION, ReporteCreate, ReporteResolucion
from app.modules.auth.repository import UsuarioRepository
from app.modules.auth.models import Usuario
from app.modules.lost.repository import LostRepository, SightingRepository
from app.modules.notifications.service import NotificationService
from app.modules.pets.repository import PetRepository

MOTIVOS_POR_TIPO = {"mascota": MOTIVOS_PUBLICACION, "perdida": MOTIVOS_PUBLICACION, "avistamiento": MOTIVOS_AVISTAMIENTO}

class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReportRepository(db)
        self.usuario_repository = UsuarioRepository(db)
        self.pet_repository = PetRepository(db)
        self.lost_repository = LostRepository(db)
        self.sighting_repository = SightingRepository(db)
        self.notification_service = NotificationService(db)

    def create_report(self, data: ReporteCreate, reportante_id: int) -> Reporte:
        if data.motivo not in MOTIVOS_POR_TIPO[data.tipo]:
            raise MotivoInvalidoException()

        objetivo_id = data.mascota_id or data.perdida_id or data.avistamiento_id
        if not self._get_objetivo(data.tipo, objetivo_id):
            raise ObjetivoInvalidoExcepcion()
        if self.repository.get_pendiente_duplicado(reportante_id, data.tipo, objetivo_id):
            raise ReporteDuplicadoException()

        reporte = Reporte(reportante_id=reportante_id, **data.model_dump())
        return self.repository.create(reporte)

    def list_reports(self, estado: str | None) -> list[Reporte]:
        return self.repository.get_by_estado(estado)

    async def resolve_report(self, reporte_id: int, data: ReporteResolucion, admin_id : int) -> Reporte:
        reporte = self.repository.get_by_id(reporte_id)
        if not reporte:
            raise ReporteNoEncontradoException()
        if reporte.estado != "pendiente":
            raise ReporteYaResueltoException()

        afectado_id = None
        if data.ocultar_contenido:
            afectado_id = self._ocultar(reporte)
            reporte.contenido_oculto = True
        if data.bloquear_usuario:
            afectado_id = afectado_id or self._get_autor(reporte)
            await self._bloquear(afectado_id, admin_id)
            reporte.usuario_bloqueado = True

        reporte.estado = data.estado
        reporte.admin_id = admin_id
        reporte.resolved_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(reporte)

        await self.notification_service.create(
            usuario_id=reporte.reportante_id, tipo="reporte_resuelto",
            mensaje="Uno de tus contenidos fue moderado por un administrador",
        )
        return reporte

    async def block_user(self, target_id: int, admin: Usuario) -> None:
        if target_id == admin.id:
            raise AccionNoPermitidaException("No puedes bloquearte a ti mismo")
        target = self.usuario_repository.get_by_id(target_id)
        if not target:
            raise UsuarioNoEncontradoException()
        if target.rol == "admin":
            raise AccionNoPermitidaException("No puedes bloquear a otro administrador")
        await self._bloquear(target_id, admin.id)

    def unblock_user(self, target_id: int, admin_id: int) -> None:
        target = self.usuario_repository.get_by_id(target_id)
        if not target:
            raise UsuarioNoEncontradoException()
        target.bloqueado = False
        target.desbloqueado_por_id = admin_id
        target.desbloqueado_at = datetime.now(timezone.utc)
        self.db.commit()

    # ----PRIVADOS--------

    def _get_objetivo(self, tipo: str, objetivo_id: int):
        if tipo == "mascota":
            return self.pet_repository.get_by_id(objetivo_id)
        if tipo == "perdida":
            return self.lost_repository.get_by_id(objetivo_id)
        return self.sighting_repository.get_by_id(objetivo_id)

    def _get_autor(self, reporte: Reporte) -> int:
        objetivo = self._get_objetivo(reporte.tipo, reporte.mascota_id or reporte.perdida_id or reporte.avistamiento_id)
        return objetivo.usuario_id

    def _ocultar(self, reporte: Reporte) -> int:
        objetivo = self._get_objetivo(reporte.tipo, reporte.mascota_id or reporte.perdida_id or reporte.avistamiento_id)
        if reporte.tipo in ("mascota", "perdida"):
            objetivo.oculta = True
        else:
            objetivo.oculto = True
        self.db.commit()
        return objetivo.usuario_id

    async def _bloquear(self, target_id: int, admin_id: int) -> None:
        target = self.usuario_repository.get_by_id(target_id)
        target.bloqueado = True
        target.bloqueado_por_id = admin_id
        target.bloqueado_at = datetime.now(timezone.utc)
        self.db.commit()
        await self.notification_service.create(
            usuario_id=target_id, tipo="cuenta_bloqueada", mensaje="Tu cuenta ha sido bloqueada por un administrador",
        )