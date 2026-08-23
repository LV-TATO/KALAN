from fastapi import APIRouter
api_router = APIRouter(prefix="/api/v1")


from app.modules.auth.router import router as auth_router
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])


from app.modules.pets.router import router as pets_router
api_router.include_router(pets_router, prefix="/pets", tags=["pets"])


from app.modules.requests.router import router as request_router
api_router.include_router(request_router, prefix="/request", tags=["request"])


from app.modules.messages.router import router as messages_router
api_router.include_router(messages_router, prefix="/messages", tags=["messages"])


from app.modules.lost.router import router as lost_router
api_router.include_router(lost_router, prefix="/lost", tags=["lost"])