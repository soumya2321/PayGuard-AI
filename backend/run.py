"""
run.py - Convenience script to start the FastAPI server.
"""

from pathlib import Path
import sys
import uvicorn

BACKEND_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_ROOT))

import config

if __name__ == "__main__":
    print(f"Starting UPI Fraud Detection Backend on http://{config.API_HOST}:{config.API_PORT}")
    uvicorn.run("app.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)
