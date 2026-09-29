"""
preprocess.py - Data loading, validation, cleaning, and scaling for UPI Fraud Detection.
"""

from typing import Tuple
import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def load_dataset(
    x_train_path: str = config.X_TRAIN_PATH,
    y_train_path: str = config.Y_TRAIN_PATH,
    x_test_path: str = config.X_TEST_PATH,
    y_test_path: str = config.Y_TEST_PATH,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Load feature matrices and labels for training and testing.
    """
    if not os.path.exists(x_train_path):
        raise FileNotFoundError(f"Missing X_train file: {x_train_path}")
    if not os.path.exists(y_train_path):
        raise FileNotFoundError(f"Missing y_train file: {y_train_path}")
    if not os.path.exists(x_test_path):
        raise FileNotFoundError(f"Missing X_test file: {x_test_path}")
    if not os.path.exists(y_test_path):
        raise FileNotFoundError(f"Missing y_test file: {y_test_path}")

    X_train = pd.read_csv(x_train_path)
    y_train = pd.read_csv(y_train_path).squeeze("columns").astype(int)
    X_test = pd.read_csv(x_test_path)
    y_test = pd.read_csv(y_test_path).squeeze("columns").astype(int)

    print(f"Loaded X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"Loaded X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")
    return X_train, y_train, X_test, y_test


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute any missing or NaN values with column median."""
    if df.isna().sum().sum() > 0:
        return df.fillna(df.median(numeric_only=True))
    return df


def clip_outliers(df: pd.DataFrame, lower_sd: float = -10.0, upper_sd: float = 10.0) -> pd.DataFrame:
    """
    Safely clip extreme outliers to prevent gradient explosion and tree skew.
    """
    return df.clip(lower=lower_sd, upper=upper_sd)


def fit_and_scale(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    feature_cols: list[str] = config.FEATURE_COLUMNS,
) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    Fit StandardScaler on X_train and transform both X_train and X_test.
    Saves scaler artifact to models/scaler.pkl.
    """
    # Ensure columns match expected feature set
    X_train_aligned = X_train[feature_cols].copy()
    X_test_aligned = X_test[feature_cols].copy()

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train_aligned),
        columns=feature_cols,
        index=X_train.index,
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test_aligned),
        columns=feature_cols,
        index=X_test.index,
    )

    os.makedirs(config.MODELS_DIR, exist_ok=True)
    joblib.dump(scaler, config.SCALER_PATH)
    print(f"StandardScaler persisted to {config.SCALER_PATH}")

    return X_train_scaled, X_test_scaled, scaler


def preprocess_pipeline() -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Executes full data preprocessing:
    1. Load raw data
    2. Handle missing values
    3. Clip extreme outliers
    4. Fit and apply feature scaling
    5. Cache processed datasets to disk
    """
    print("\n--- Starting Data Preprocessing Pipeline ---")
    X_train, y_train, X_test, y_test = load_dataset()

    # Impute missing values
    X_train = handle_missing_values(X_train)
    X_test = handle_missing_values(X_test)

    # Clip outliers
    X_train = clip_outliers(X_train)
    X_test = clip_outliers(X_test)

    # Scale features
    X_train_scaled, X_test_scaled, _ = fit_and_scale(X_train, X_test)

    # Persist processed copies
    os.makedirs(config.DATA_PROCESSED_DIR, exist_ok=True)
    X_train_scaled.to_csv(config.X_TRAIN_PROCESSED, index=False)
    X_test_scaled.to_csv(config.X_TEST_PROCESSED, index=False)
    print(f"Processed datasets successfully saved to {config.DATA_PROCESSED_DIR}")

    return X_train_scaled, y_train, X_test_scaled, y_test


if __name__ == "__main__":
    X_tr, y_tr, X_te, y_te = preprocess_pipeline()
    print("Preprocessing completed successfully.")
