import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.core.database import SessionLocal
from app.modules.auth.session_history_repository import SesionHistoryRepository
from app.modules.auth.session_store import session_exists

logger = logging.getLogger("kalan.scheduler")

scheduler = AsyncIOScheduler()

def _sweep_expired_sessions() -> None:
    db = SessionLocal()
    try:
        repository = SesionHistoryRepository(db)
        for registro in repository.get_open_sessions():
            try:
                if not session_exists(registro.session_hash):
                    repository.end(registro.session_hash, "inactividad")
            except Exception:
                logger.exception("Error verificando en Redis la sesion %s", registro.session_hash)
    except Exception:
        logger.exception("Error ejecutando el barrido de sesiones expiradas")
    finally:
        db.close()

def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.add_job(
            _sweep_expired_sessions,
            trigger=IntervalTrigger(minutes=settings.session_sweep_interval_minutes),
            id="sweep_expired_sessions",
            replace_existing=True,
        )
        scheduler.start()

def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=True)