from fastapi import APIRouter

from app.modules.auth.router import router as auth_router

from app.modules.pets.router import router as pets_router

from app.modules.requests.router import router as request_router

from app.modules.messages.router import router as messages_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

api_router.include_router(pets_router, prefix="/pets", tags=["pets"])

api_router.include_router(request_router, prefix="/request", tags=["request"])

api_router.include_router(messages_router, prefix="/messages", tags=["messages"])