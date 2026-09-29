"""
config.py - Centralized configuration for the Backend API & Machine Learning pipeline.
Manages file paths, model parameters, database connections, and environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# ── Base paths (backend -> project root) ──────────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

DATA_DIR       = PROJECT_ROOT / "data"
DATA_RAW_DIR   = DATA_DIR / "raw"
DATA_PROC_DIR  = DATA_DIR / "processed"
MODELS_DIR     = PROJECT_ROOT / "models"
REPORTS_DIR    = PROJECT_ROOT / "reports"
FIGURES_DIR    = REPORTS_DIR / "figures"

# ── Data file paths ──────────────────────────────────────────────────────────
X_TRAIN_PATH = DATA_RAW_DIR / "X_train.csv"
X_TEST_PATH  = DATA_RAW_DIR / "X_test.csv"
Y_TRAIN_PATH = DATA_RAW_DIR / "y_train.csv"
Y_TEST_PATH  = DATA_RAW_DIR / "y_test.csv"

# Fallback paths if data is in project root
if not X_TRAIN_PATH.exists() and (PROJECT_ROOT / "X_train.csv").exists():
    X_TRAIN_PATH = PROJECT_ROOT / "X_train.csv"
    X_TEST_PATH  = PROJECT_ROOT / "X_test.csv"
    Y_TRAIN_PATH = PROJECT_ROOT / "y_train.csv"
    Y_TEST_PATH  = PROJECT_ROOT / "y_test.csv"

X_TRAIN_PROCESSED = DATA_PROC_DIR / "X_train_processed.csv"
X_TEST_PROCESSED  = DATA_PROC_DIR / "X_test_processed.csv"

# ── Model artifact paths ─────────────────────────────────────────────────────
MODEL_PATH             = MODELS_DIR / "model.pkl"
SCALER_PATH            = MODELS_DIR / "scaler.pkl"
METRICS_PATH           = MODELS_DIR / "metrics.json"
FEATURES_PATH          = MODELS_DIR / "features.json"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "feature_importance.json"

# ── Feature schema ───────────────────────────────────────────────────────────
FEATURE_COLUMNS = [
    "amount",
    "session_duration",
    "receiver_transaction_history",
    "transaction_amount_vs_sender_history",
    "geographic_disparity",
    "transaction_time_of_day",
    "time_between_link_click_and_transaction",
    "input_timing_consistency",
    "keyboard_input_speed",
    "input_pause_patterns",
    "screen_active_time",
    "geographic_location_vs_ip",
    "background_data_usage",
    "pin_entry_speed",
    "request_amount_roundness",
    "request_acceptance_rate",
    "time_to_respond_to_request",
    "user_id_freq",
]

TARGET_COLUMN = "is_fraud"

# ── Risk Calibration Thresholds ──────────────────────────────────────────────
RISK_THRESHOLD_LOW  = float(os.getenv("RISK_THRESHOLD_LOW", "0.35"))
RISK_THRESHOLD_HIGH = float(os.getenv("RISK_THRESHOLD_HIGH", "0.70"))

# ── Server & DB settings ─────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG    = os.getenv("DEBUG", "True").lower() == "true"

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SQLITE_DB_PATH = DATA_DIR / "upi_fraud.db"
