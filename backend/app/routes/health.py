"""
health.py - Health check route for backend service monitoring.
"""

from fastapi import APIRouter
from app.services.db_service import get_db_service
from app.utils.constants import EDUCATIONAL_DISCLAIMER
import config

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    db = get_db_service()
    analytics_data = db.get_dashboard_analytics()
    return {
        "status": "operational",
        "service": "UPI Fraud Detection API",
        "version": "2.0.0",
        "model_file": config.MODEL_PATH.name,
        "database_backend": "Supabase PostgreSQL" if db.use_supabase else "Local SQLite (Ready for Supabase)",
        "database_connected": True,
        "total_records_in_db": analytics_data["summary"]["total_transactions"],
        "pending_critical_alerts": analytics_data["summary"]["pending_critical_alerts"],
        "disclaimer": EDUCATIONAL_DISCLAIMER,
    }
