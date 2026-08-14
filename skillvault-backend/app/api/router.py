from fastapi import APIRouter

from app.api.v1.executions import router as executions_router
from app.api.v1.health import router as health_router
from app.api.v1.skills import router as skills_router
from app.api.v1.tasks import router as tasks_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(tasks_router)
api_router.include_router(skills_router)
api_router.include_router(executions_router)
