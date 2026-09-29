"""
config.py - Central configuration for the UPI Fraud Detection project.
All paths, hyperparameters, and settings are managed here.
"""

import os

# ── Base paths ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_RAW_DIR       = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR         = os.path.join(BASE_DIR, "models")
REPORTS_DIR        = os.path.join(BASE_DIR, "reports")
FIGURES_DIR        = os.path.join(REPORTS_DIR, "figures")

# ── Data file paths ──────────────────────────────────────────────────────────
X_TRAIN_PATH = os.path.join(DATA_RAW_DIR, "X_train.csv")
X_TEST_PATH  = os.path.join(DATA_RAW_DIR, "X_test.csv")
Y_TRAIN_PATH = os.path.join(DATA_RAW_DIR, "y_train.csv")
Y_TEST_PATH  = os.path.join(DATA_RAW_DIR, "y_test.csv")

X_TRAIN_PROCESSED = os.path.join(DATA_PROCESSED_DIR, "X_train_processed.csv")
X_TEST_PROCESSED  = os.path.join(DATA_PROCESSED_DIR, "X_test_processed.csv")

# ── Model artifact paths ─────────────────────────────────────────────────────
MODEL_PATH             = os.path.join(MODELS_DIR, "model.pkl")
SCALER_PATH            = os.path.join(MODELS_DIR, "scaler.pkl")
METRICS_PATH           = os.path.join(MODELS_DIR, "metrics.json")
FEATURES_PATH          = os.path.join(MODELS_DIR, "features.json")
FEATURE_IMPORTANCE_PATH = os.path.join(MODELS_DIR, "feature_importance.json")

# ── Feature columns (matching X_test.csv) ────────────────────────────────────
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

# ── Risk Thresholds ─────────────────────────────────────────────────────────
RISK_THRESHOLD_LOW  = 0.35  # Below this: Low Risk (Legitimate)
RISK_THRESHOLD_HIGH = 0.70  # Above this: High Risk (Suspected Fraud)
# Between LOW and HIGH: Moderate Risk (Flag for Review)

# ── Model hyperparameters ─────────────────────────────────────────────────────
RANDOM_FOREST_PARAMS = {
    "n_estimators": 200,
    "max_depth": 12,
    "min_samples_split": 4,
    "min_samples_leaf": 2,
    "class_weight": "balanced",
    "random_state": 42,
    "n_jobs": -1,
}

XGBOOST_PARAMS = {
    "n_estimators": 200,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "eval_metric": "logloss",
    "random_state": 42,
}

# ── Training settings ─────────────────────────────────────────────────────────
TEST_SIZE    = 0.2
RANDOM_STATE = 42

# ── Server & DB settings ──────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG    = os.getenv("DEBUG", "True").lower() == "true"

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SQLITE_DB_PATH = os.path.join(BASE_DIR, "data", "upi_fraud.db")

