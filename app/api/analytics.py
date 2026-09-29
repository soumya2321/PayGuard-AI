"""
analytics.py - REST endpoints for authentic dashboard analytics, trends, and risk distributions.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.analytics import DashboardAnalyticsResponse
from app.services.db_service import get_db_service

router = APIRouter(prefix="/analytics", tags=["Fraud Analytics Dashboard"])


@router.get("/dashboard", response_model=DashboardAnalyticsResponse, summary="Retrieve dynamic dashboard analytics")
async def get_dashboard_metrics():
    """
    Returns authentic summary metrics aggregated directly from the database:
    - Total transactions, fraud counts, and average risk score
    - Risk tier breakdown (Low, Moderate, High)
    - Volume distribution in INR
    - Time-series trends of daily transaction volume and fraud rates
    - Top observed behavioral drivers
    """
    try:
        db = get_db_service()
        data = db.get_dashboard_analytics()
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard analytics: {str(e)}"
        )
