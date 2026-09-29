"""
train.py - Production model training pipeline for UPI Fraud Detection.
Handles class imbalance via SMOTE and cost-sensitive weighting,
evaluates Random Forest and XGBoost with Stratified K-Fold CV,
and exports all artifacts, metrics, and visualization plots.
"""

from typing import Tuple, Dict, Any
import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.preprocess import preprocess_pipeline
from src.features import add_behavioral_features
from src.evaluate import run_full_evaluation, compute_metrics


def balance_training_data(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    target_ratio: float = 0.5,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Handle class imbalance using SMOTE over-sampling on the minority class.
    target_ratio=0.5 brings fraud cases to 50% of legitimate cases,
    avoiding synthetic noise while strengthening minority class decision boundaries.
    """
    print(f"\nOriginal training class balance: {dict(y_train.value_counts())}")
    smote = SMOTE(sampling_strategy=target_ratio, random_state=config.RANDOM_STATE)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    print(f"Resampled training class balance (via SMOTE): {dict(pd.Series(y_resampled).value_counts())}")
    return pd.DataFrame(X_resampled, columns=X_train.columns), pd.Series(y_resampled)


def train_random_forest(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """Train Random Forest classifier with hyperparameter config."""
    print("\n[1/2] Training Random Forest Classifier...")
    model = RandomForestClassifier(**config.RANDOM_FOREST_PARAMS)
    model.fit(X_train, y_train)
    return model


def train_xgboost(X_train: pd.DataFrame, y_train: pd.Series) -> XGBClassifier:
    """Train XGBoost classifier with imbalance-aware scale_pos_weight."""
    print("\n[2/2] Training XGBoost Classifier...")
    neg_count = sum(y_train == 0)
    pos_count = sum(y_train == 1)
    scale_pos = neg_count / max(pos_count, 1)

    xgb_params = {**config.XGBOOST_PARAMS, "scale_pos_weight": scale_pos}
    model = XGBClassifier(**xgb_params)
    model.fit(X_train, y_train, verbose=False)
    return model


def run_cross_validation(model, X: pd.DataFrame, y: pd.Series, model_name: str, cv: int = 5) -> float:
    """Run stratified K-fold cross-validation using ROC-AUC metric."""
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=config.RANDOM_STATE)
    scores = cross_val_score(model, X, y, cv=skf, scoring="roc_auc", n_jobs=-1)
    print(f"  {model_name} 5-Fold Cross-Val ROC-AUC: {scores.mean():.4f} (+/- {scores.std():.4f})")
    return float(scores.mean())


def run_training_pipeline() -> Dict[str, Any]:
    """
    Full End-to-End ML Pipeline:
      1. Preprocess & Scale
      2. Domain Feature Engineering
      3. Class Imbalance Mitigation (SMOTE)
      4. Model Training & Cross-Validation (RF vs XGBoost)
      5. Test Set Evaluation & Model Selection
      6. Artifact Serialization (Model, Scaler, Features, Metrics, Figures)
    """
    print("=" * 65)
    print("   UPI FRAUD DETECTION SYSTEM — MACHINE LEARNING PIPELINE")
    print("=" * 65)

    # 1. Preprocess
    X_train, y_train, X_test, y_test = preprocess_pipeline()

    # 2. Feature engineering
    print("\nApplying behavioral feature engineering...")
    X_train = add_behavioral_features(X_train)
    X_test = add_behavioral_features(X_test)
    feature_names = list(X_train.columns)
    print(f"Total features after engineering: {len(feature_names)}")

    # Persist feature column list
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    with open(config.FEATURES_PATH, "w") as f:
        json.dump(feature_names, f, indent=2)
    print(f"Feature schema persisted to {config.FEATURES_PATH}")

    # 3. Handle class imbalance on training split
    X_train_balanced, y_train_balanced = balance_training_data(X_train, y_train, target_ratio=0.5)

    # 4. Train both candidate architectures
    rf_model = train_random_forest(X_train_balanced, y_train_balanced)
    xgb_model = train_xgboost(X_train_balanced, y_train_balanced)

    # 5. Cross-validate on resampled data
    print("\nCross-validating candidate models...")
    rf_cv_auc = run_cross_validation(rf_model, X_train_balanced, y_train_balanced, "Random Forest")
    xgb_cv_auc = run_cross_validation(xgb_model, X_train_balanced, y_train_balanced, "XGBoost")

    # 6. Evaluate both on pristine held-out test set
    print("\nEvaluating on Held-Out Test Set (Unseen Transactions)...")
    rf_test_prob = rf_model.predict_proba(X_test)[:, 1]
    xgb_test_prob = xgb_model.predict_proba(X_test)[:, 1]

    from sklearn.metrics import roc_auc_score, f1_score
    rf_test_auc = roc_auc_score(y_test, rf_test_prob)
    xgb_test_auc = roc_auc_score(y_test, xgb_test_prob)

    rf_test_f1 = f1_score(y_test, rf_model.predict(X_test), zero_division=0)
    xgb_test_f1 = f1_score(y_test, xgb_model.predict(X_test), zero_division=0)

    print(f"  Random Forest -> Test ROC-AUC: {rf_test_auc:.4f} | Test F1: {rf_test_f1:.4f}")
    print(f"  XGBoost       -> Test ROC-AUC: {xgb_test_auc:.4f} | Test F1: {xgb_test_f1:.4f}")

    # Champion selection: prefer highest Test ROC-AUC
    if rf_test_auc >= xgb_test_auc:
        champion_model = rf_model
        champion_name = "Random Forest Classifier"
        best_auc = rf_test_auc
    else:
        champion_model = xgb_model
        champion_name = "XGBoost Classifier"
        best_auc = xgb_test_auc

    print(f"\n>>> Selected Champion Model: {champion_name} (Test AUC = {best_auc:.4f})")

    # 7. Persist champion model
    joblib.dump(champion_model, config.MODEL_PATH)
    print(f"Champion model persisted to {config.MODEL_PATH}")

    # 8. Full evaluation & figure generation
    metrics = run_full_evaluation(champion_model, X_test, y_test, feature_names)
    metrics["model_name"] = champion_name
    metrics["cv_roc_auc"] = round(rf_cv_auc if champion_model == rf_model else xgb_cv_auc, 4)

    # Re-save metrics with model_name
    with open(config.METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print("\nTraining and evaluation pipeline completed successfully!")
    return metrics


if __name__ == "__main__":
    run_training_pipeline()
