"""
main.py - Entry point for the FastAPI backend application.
"""

from pathlib import Path
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend root is in Python path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

import config
from app.database import engine, Base
from app.models.schema_models import *  # ensure all models registered
from app.seed_data import seed_database
from app.routes import health, predict, model, payguard_routes
from app.routers import auth
from app.utils.constants import EDUCATIONAL_DISCLAIMER

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed baseline records
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title="PayGuard AI - Intelligent UPI Fraud Detection System API",
    description=(
        "Production-style REST and WebSocket API for real-time UPI transaction fraud detection "
        "incorporating Behavioral Analysis, Receiver Risk Scoring, ML Classification, and Real-Time Monitoring.\n\n"
        f"**Academic Prototype Disclaimer:** {EDUCATIONAL_DISCLAIMER}"
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# Enable CORS for local Vite and production clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication routes (mounted both at root and /api)
app.include_router(auth.router)
app.include_router(auth.router, prefix="/api")

# Core PayGuard routes mounted both at root and /api for seamless frontend compatibility
app.include_router(payguard_routes.router)
app.include_router(payguard_routes.router, prefix="/api")

# Supplemental legacy/model routes
app.include_router(health.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(model.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "system": "PayGuard AI - Intelligent UPI Fraud Detection System",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/health",
        "layers": {
            "presentation": "React 19 + Vite + Tailwind CSS",
            "backend": "FastAPI + SQLAlchemy",
            "machine_learning": "Behavioral Analysis + Receiver Risk + XGBoost/RF",
            "monitoring": "WebSocket /ws/monitor",
            "database": "PostgreSQL / SQLite",
        },
        "disclaimer": EDUCATIONAL_DISCLAIMER,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)
