from fastapi import APIRouter, Depends
from app.api.deps import get_analytics_service
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", summary="Get dashboard overview metrics")
async def get_overview(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.get_overview_metrics()


@router.get("/capability-gaps", summary="List detected capability gaps")
async def get_capability_gaps(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.get_capability_gaps()
