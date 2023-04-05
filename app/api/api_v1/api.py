from fastapi import APIRouter

from app.api.api_v1.endpoints import stats

api_router = APIRouter()
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
