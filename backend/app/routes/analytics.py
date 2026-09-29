"""
analytics.py - REST endpoints for authentic dashboard analytics and metrics.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.analytics import DashboardAnalyticsResponse
from app.services.db_service import get_db_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
async def get_dashboard_metrics():
    try:
        db = get_db_service()
        data = db.get_dashboard_analytics()
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard analytics: {str(e)}"
        )
