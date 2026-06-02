from fastapi import APIRouter
from src.core.config import settings

router = APIRouter(tags=["Main API V1"])


@router.get("/info")
async def get_info():
    return {
        "name": "High Performance Bot API",
        "version": "0.1.0",
        "status": "running",
        "env": settings.ENV,
    }


@router.get("/health")
async def health_check():
    return {"status": "ok", "bot": settings.username}
