from fastapi import APIRouter

from app.api.v1 import analytics, executions, health, skills, tasks, workflows

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(tasks.router)
api_router.include_router(skills.router)
api_router.include_router(executions.router)
api_router.include_router(workflows.router)
api_router.include_router(analytics.router)
