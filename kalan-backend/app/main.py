from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.scheduler import start_scheduler, stop_scheduler

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"]
)

register_exception_handlers(app)
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.exception_handler(RequestValidationError)
async def errores_validacion(
    request: Request,
    exc: RequestValidationError
):

    mensajes = {
        "missing": "Este campo es obligatorio.",
        "string_type": "Debe enviar un texto.",
        "string_too_short": "El texto no alcanza la longitud mínima permitida.",
        "string_too_long": "El texto supera la longitud máxima permitida.",
        "bool_parsing": "Debe enviar un valor booleano válido: true o false.",
        "bool_type": "Debe enviar un valor booleano: true o false.",
        "list_type": "Debe enviar una lista.",
        "too_long": "Se supera la cantidad máxima de elementos permitida.",
        "literal_error": "El valor no está entre las opciones permitidas.",
        "url_parsing": "Debe enviar una URL válida.",
        "url_scheme": "El protocolo de la URL no está permitido.",
    }

    errores = []

    for error in exc.errors():
        tipo = error["type"]
        ubicacion = list(error["loc"])

        if tipo == "json_invalid":
            causa = error.get("ctx", {}).get("error")

            mensaje = (
                "El JSON está mal formado: se esperaba un valor. "
                "Revise que cada propiedad tenga un valor después "
                "de los dos puntos."
                if causa == "Expecting value"
                else (
                    "El JSON está mal formado. "
                    "Revise las comillas, comas, llaves y valores."
                )
            )

        elif tipo == "value_error" and isinstance(
            error.get("ctx", {}).get("error", ValueError)
        ):
            mensaje = str(error["ctx"]["error"])
        else:
            mensaje = mensajes.get(
                tipo,
                "El valor enviado no cumple las reglas de validación.",
            )

        errores.append({
            "type": tipo,
            "loc": ubicacion,
            "msg": mensaje,
        })

    return JSONResponse(
        status_code=422,
        content={"detail": errores},
    )