"""
alerts.py - REST endpoints for alert monitoring and analyst review.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.alert import AlertRecord, AlertUpdate
from app.services.db_service import get_db_service

router = APIRouter(prefix="/alerts", tags=["Fraud Alerts"])


@router.get("", response_model=List[AlertRecord])
async def list_alerts(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
):
    try:
        db = get_db_service()
        alerts = db.get_alerts(status=status_filter, severity=severity, limit=limit)
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alerts: {str(e)}"
        )


@router.patch("/{alert_id}", response_model=AlertRecord)
async def update_alert(alert_id: str, payload: AlertUpdate):
    try:
        db = get_db_service()
        updated = db.update_alert(alert_id=alert_id, status=payload.status, notes=payload.analyst_notes)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert '{alert_id}' not found.")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert: {str(e)}"
        )
