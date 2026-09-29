"""
preprocess.py - Preprocessing, data cleaning, and feature scaling.
"""

from typing import Tuple
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

# Ensure config can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def load_dataset() -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Load feature matrices and labels for training and testing."""
    X_train = pd.read_csv(config.X_TRAIN_PATH)
    y_train = pd.read_csv(config.Y_TRAIN_PATH).squeeze("columns").astype(int)
    X_test = pd.read_csv(config.X_TEST_PATH)
    y_test = pd.read_csv(config.Y_TEST_PATH).squeeze("columns").astype(int)
    return X_train, y_train, X_test, y_test


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute any missing or NaN values with column median."""
    if df.isna().sum().sum() > 0:
        return df.fillna(df.median(numeric_only=True))
    return df


def clip_outliers(df: pd.DataFrame, lower_sd: float = -10.0, upper_sd: float = 10.0) -> pd.DataFrame:
    """Safely clip extreme outliers to prevent gradient explosion."""
    return df.clip(lower=lower_sd, upper=upper_sd)


def fit_and_scale(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    feature_cols: list[str] = config.FEATURE_COLUMNS,
) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """Fit StandardScaler on X_train and transform train & test."""
    X_train_aligned = X_train[feature_cols].copy()
    X_test_aligned = X_test[feature_cols].copy()

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train_aligned), columns=feature_cols, index=X_train.index)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test_aligned), columns=feature_cols, index=X_test.index)

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, config.SCALER_PATH)
    return X_train_scaled, X_test_scaled, scaler


def preprocess_pipeline() -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Full preprocessing pipeline."""
    X_train, y_train, X_test, y_test = load_dataset()
    X_train = clip_outliers(handle_missing_values(X_train))
    X_test = clip_outliers(handle_missing_values(X_test))
    X_train_scaled, X_test_scaled, _ = fit_and_scale(X_train, X_test)
    return X_train_scaled, y_train, X_test_scaled, y_test
