"""
main.py - Production FastAPI backend for UPI Fraud Detection System.
Provides RESTful APIs for real-time risk scoring, transaction simulation,
analytics aggregation, alert management, and model governance.
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from app.api import predict, transactions, alerts, analytics, model
from app.services.db_service import get_db_service

app = FastAPI(
    title="UPI Fraud Detection System API",
    description=(
        "Production-grade REST API for detecting fraudulent UPI transactions "
        "using behavioral telemetry, contextual anomaly detection, and machine learning. "
        "\n\n**Educational Disclaimer:** This system provides probabilistic fraud-risk indications "
        "for decision support and educational exploration. It does not provide absolute guarantees."
    ),
    version="2.0.0",
)

# ── Cross-Origin Resource Sharing (CORS) ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Vite dev server & production builds
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Routers under /api ──────────────────────────────────────────────────
app.include_router(predict.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(model.router, prefix="/api")


# ── Health & System Status Endpoint ──────────────────────────────────────────
@app.get("/api/health", tags=["System Health"])
async def health_check():
    """
    System status and operational mode check.
    """
    db = get_db_service()
    analytics_data = db.get_dashboard_analytics()
    return {
        "status": "operational",
        "service": "UPI Fraud Detection API",
        "version": "2.0.0",
        "model_file": os.path.basename(config.MODEL_PATH),
        "database_backend": "Supabase PostgreSQL" if db.use_supabase else "Local SQLite (Ready for Supabase)",
        "database_connected": True,
        "total_records_in_db": analytics_data["summary"]["total_transactions"],
        "pending_critical_alerts": analytics_data["summary"]["pending_critical_alerts"],
        "disclaimer": (
            "Educational Fraud-Risk Detection System: Output provides probabilistic risk scores. "
            "Not an absolute guarantee of fraud or legitimacy."
        ),
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "UPI Fraud Detection System API is live.",
        "documentation": "/docs",
        "health": "/api/health",
        "analytics": "/api/analytics/dashboard",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)
