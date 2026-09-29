"""
preprocessing.py - Data preprocessing, cleaning, scaling, and feature engineering
for the UPI Fraud Detection Machine Learning Pipeline.
"""

from typing import Tuple, List, Dict, Any, Optional
from pathlib import Path
import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# Root path resolution
ML_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ML_DIR.parent
ARTIFACTS_DIR = ML_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Base feature schema
BASE_FEATURE_COLUMNS = [
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


def load_raw_dataset(data_dir: Optional[Path] = None) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Step 1: Load raw training and testing CSV datasets.
    """
    if data_dir is None:
        data_dir = DATA_RAW_DIR
        if not (data_dir / "X_train.csv").exists() and (PROJECT_ROOT / "X_train.csv").exists():
            data_dir = PROJECT_ROOT

    x_train_file = data_dir / "X_train.csv"
    y_train_file = data_dir / "y_train.csv"
    x_test_file = data_dir / "X_test.csv"
    y_test_file = data_dir / "y_test.csv"

    for file_path in [x_train_file, y_train_file, x_test_file, y_test_file]:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset file missing: {file_path}. Please place required CSVs in data/raw/."
            )

    X_train = pd.read_csv(x_train_file)
    y_train = pd.read_csv(y_train_file).squeeze("columns").astype(int)
    X_test = pd.read_csv(x_test_file)
    y_test = pd.read_csv(y_test_file).squeeze("columns").astype(int)

    print(f"[1. Load Dataset] Loaded X_train: {X_train.shape}, y_train: {y_train.shape}")
    print(f"[1. Load Dataset] Loaded X_test:  {X_test.shape}, y_test:  {y_test.shape}")
    return X_train, y_train, X_test, y_test


def inspect_dataset(df: pd.DataFrame, name: str = "Dataset") -> Dict[str, Any]:
    """
    Step 2: Inspect columns, types, memory usage, and basic distributions.
    """
    info = {
        "name": name,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": {col: int(df[col].isna().sum()) for col in df.columns},
    }
    print(f"[2. Inspect] {name}: {df.shape[0]} samples x {df.shape[1]} features.")
    return info


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3: Handle missing values with median imputation for numerical features.
    """
    df_clean = df.copy()
    null_count = df_clean.isna().sum().sum()
    if null_count > 0:
        print(f"[3. Missing Values] Found {null_count} missing entries. Imputing with column medians...")
        df_clean = df_clean.fillna(df_clean.median(numeric_only=True))
    else:
        print("[3. Missing Values] No missing values detected.")
    return df_clean


def remove_duplicates(X: pd.DataFrame, y: Optional[pd.Series] = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
    """
    Step 4: Detect and remove duplicate records.
    """
    if y is not None:
        combined = pd.concat([X, y], axis=1)
        init_len = len(combined)
        combined = combined.drop_duplicates()
        dropped = init_len - len(combined)
        print(f"[4. Duplicates] Removed {dropped} duplicate rows.")
        y_clean = combined.iloc[:, -1]
        X_clean = combined.iloc[:, :-1]
        return X_clean, y_clean
    else:
        init_len = len(X)
        X_clean = X.drop_duplicates()
        dropped = init_len - len(X_clean)
        print(f"[4. Duplicates] Removed {dropped} duplicate rows.")
        return X_clean, None


def detect_and_clean_invalid_values(
    df: pd.DataFrame,
    lower_bound: float = -10.0,
    upper_bound: float = 10.0,
) -> pd.DataFrame:
    """
    Step 5: Detect invalid values (Infs, extreme anomalies) and clip safely.
    """
    df_clean = df.copy()
    # Replace infinities
    df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
    df_clean = df_clean.fillna(df_clean.median(numeric_only=True))
    # Clip extreme outlier values to prevent skew
    df_clean = df_clean.clip(lower=lower_bound, upper=upper_bound)
    print(f"[5. Invalid Values] Cleaned infs/NaNs and clipped outliers within [{lower_bound}, {upper_bound}].")
    return df_clean


def encode_categorical_variables(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Step 6: Detect any categorical/string columns and one-hot encode them.
    If already purely numerical, passes through gracefully.
    """
    df_encoded = df.copy()
    cat_cols = df_encoded.select_dtypes(include=["object", "category"]).columns.tolist()
    encoders = {}

    if cat_cols:
        print(f"[6. Categorical Encoding] Detected categorical columns: {cat_cols}. Encoding...")
        df_encoded = pd.get_dummies(df_encoded, columns=cat_cols, drop_first=True)
    else:
        print("[6. Categorical Encoding] All features are numerical. No categorical encoding needed.")

    return df_encoded, encoders


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 8: Domain behavioral, interaction, and ratio feature engineering for UPI fraud.
    """
    print("[8. Feature Engineering] Engineering domain behavioral and velocity features...")
    df_eng = df.copy()

    # 1. Speed-timing interaction: rapid entry with hesitation pauses
    if "keyboard_input_speed" in df_eng.columns and "input_pause_patterns" in df_eng.columns:
        df_eng["speed_pause_interaction"] = (
            df_eng["keyboard_input_speed"] * df_eng["input_pause_patterns"]
        ).clip(-20.0, 20.0)

    # 2. Combined geographic risk score (GPS disparity + IP location mismatch)
    if "geographic_disparity" in df_eng.columns and "geographic_location_vs_ip" in df_eng.columns:
        df_eng["geo_risk_score"] = (
            df_eng["geographic_disparity"] + df_eng["geographic_location_vs_ip"]
        ).clip(-10.0, 10.0)

    # 3. Amount anomaly: amount scaled by historical sender deviation
    if "amount" in df_eng.columns and "transaction_amount_vs_sender_history" in df_eng.columns:
        df_eng["amount_anomaly"] = (
            df_eng["amount"] * df_eng["transaction_amount_vs_sender_history"]
        ).clip(-50.0, 50.0)

    # 4. Session velocity: transfer amount relative to session duration
    if "amount" in df_eng.columns and "session_duration" in df_eng.columns:
        safe_duration = df_eng["session_duration"].apply(lambda v: v if abs(v) > 0.05 else np.nan)
        df_eng["amount_per_session"] = (df_eng["amount"] / safe_duration).fillna(0.0).clip(-20.0, 20.0)

    # 5. Fast response flag (scripted / coerced approvals)
    if "time_to_respond_to_request" in df_eng.columns:
        df_eng["is_fast_response"] = (df_eng["time_to_respond_to_request"] < -0.8).astype(float)

    # 6. Round amount flag (common in scam requests)
    if "request_amount_roundness" in df_eng.columns:
        df_eng["is_round_amount"] = (df_eng["request_amount_roundness"] > 0.5).astype(float)

    # 7. Device / Network anomaly (high background telemetry + location mismatch)
    if "background_data_usage" in df_eng.columns and "geographic_location_vs_ip" in df_eng.columns:
        df_eng["device_network_risk"] = (
            df_eng["background_data_usage"] * (df_eng["geographic_location_vs_ip"] + 1.0)
        ).clip(-20.0, 20.0)

    # 8. Input anomaly index (inconsistent cadence vs abnormal PIN velocity)
    if "input_timing_consistency" in df_eng.columns and "pin_entry_speed" in df_eng.columns:
        df_eng["input_irregularity"] = (
            df_eng["pin_entry_speed"] - df_eng["input_timing_consistency"]
        ).clip(-10.0, 10.0)

    return df_eng


def scale_numerical_features(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    save_path: Optional[Path] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    Step 7: Fit StandardScaler on training features and transform train and test.
    Saves preprocessor artifact to disk.
    """
    print("[7. Feature Scaling] Fitting StandardScaler on training set...")
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns, index=X_test.index)

    if save_path is None:
        save_path = ARTIFACTS_DIR / "preprocessor.joblib"

    joblib.dump(scaler, save_path)
    print(f"[7. Feature Scaling] Saved fitted scaler to {save_path}")

    # Also sync to models/scaler.pkl for backend compatibility
    models_scaler_path = PROJECT_ROOT / "models" / "scaler.pkl"
    models_scaler_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, models_scaler_path)

    return X_train_scaled, X_test_scaled, scaler


def handle_class_imbalance(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    sampling_strategy: float = 0.5,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Step 11: Handle class imbalance via SMOTE over-sampling.
    Brings minority fraud class to target ratio without synthetic noise explosion.
    """
    original_counts = dict(pd.Series(y_train).value_counts())
    print(f"[11. Class Imbalance] Original class distribution: {original_counts}")

    smote = SMOTE(sampling_strategy=sampling_strategy, random_state=random_state)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    resampled_counts = dict(pd.Series(y_resampled).value_counts())
    print(f"[11. Class Imbalance] Resampled class distribution (SMOTE): {resampled_counts}")

    return pd.DataFrame(X_resampled, columns=X_train.columns), pd.Series(y_resampled)


def full_preprocessing_pipeline() -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, List[str]]:
    """
    Executes all preprocessing steps in systematic sequence:
    1. Load raw dataset
    2. Inspect columns
    3. Handle missing values
    4. Remove duplicates
    5. Clean invalid values
    6. Encode categorical features
    7. Scale numerical features
    8. Engineer features
    9. Separate features and target
    10. Prepare train/test splits
    11. Handle class imbalance on train split
    """
    print("\n" + "=" * 65)
    print("   STEP-BY-STEP DATA PREPROCESSING & CLEANING PIPELINE")
    print("=" * 65)

    # 1. Load
    X_train, y_train, X_test, y_test = load_raw_dataset()

    # 2. Inspect
    inspect_dataset(X_train, "X_train")
    inspect_dataset(X_test, "X_test")

    # 3. Missing values
    X_train = handle_missing_values(X_train)
    X_test = handle_missing_values(X_test)

    # 4. Remove duplicates
    X_train, y_train = remove_duplicates(X_train, y_train)
    X_test, y_test = remove_duplicates(X_test, y_test)

    # 5. Clean invalid values
    X_train = detect_and_clean_invalid_values(X_train)
    X_test = detect_and_clean_invalid_values(X_test)

    # 6. Encode categorical
    X_train, _ = encode_categorical_variables(X_train)
    X_test, _ = encode_categorical_variables(X_test)

    # 7. Scale
    X_train_scaled, X_test_scaled, _ = scale_numerical_features(X_train, X_test)

    # 8. Feature engineering
    X_train_eng = engineer_features(X_train_scaled)
    X_test_eng = engineer_features(X_test_scaled)
    feature_names = list(X_train_eng.columns)

    # Save feature names list
    with open(ARTIFACTS_DIR / "feature_names.json", "w") as f:
        import json
        json.dump(feature_names, f, indent=2)

    # 11. Handle class imbalance on training set only (prevent data leakage into test set)
    X_train_final, y_train_final = handle_class_imbalance(X_train_eng, y_train, sampling_strategy=0.5, random_state=42)

    print("=" * 65)
    print(f"Preprocessing complete. Total features: {len(feature_names)}")
    print(f"Final training set: {X_train_final.shape}, Final test set: {X_test_eng.shape}")
    print("=" * 65 + "\n")

    return X_train_final, y_train_final, X_test_eng, y_test, feature_names


if __name__ == "__main__":
    full_preprocessing_pipeline()
