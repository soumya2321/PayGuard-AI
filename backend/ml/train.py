"""
train.py - Production model training script.
"""

from typing import Tuple, Dict, Any
from pathlib import Path
import sys
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from ml.preprocess import preprocess_pipeline
from ml.features import add_behavioral_features
from ml.evaluate import compute_metrics


def run_training_pipeline() -> Dict[str, Any]:
    """Train XGBoost/RF on SMOTE-balanced data and save champion model."""
    X_train, y_train, X_test, y_test = preprocess_pipeline()
    X_train = add_behavioral_features(X_train)
    X_test = add_behavioral_features(X_test)
    feature_names = list(X_train.columns)

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.FEATURES_PATH, "w") as f:
        json.dump(feature_names, f, indent=2)

    smote = SMOTE(sampling_strategy=0.5, random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    neg_count = sum(y_train_res == 0)
    pos_count = sum(y_train_res == 1)
    scale_pos = neg_count / max(pos_count, 1)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        scale_pos_weight=scale_pos,
        random_state=42,
    )
    model.fit(X_train_res, y_train_res, verbose=False)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = compute_metrics(y_test, y_pred, y_prob)
    metrics["model_name"] = "XGBoost Classifier"

    joblib.dump(model, config.MODEL_PATH)
    with open(config.METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    importances = {feat: round(float(imp), 5) for feat, imp in zip(feature_names, model.feature_importances_)}
    with open(config.FEATURE_IMPORTANCE_PATH, "w") as f:
        json.dump(importances, f, indent=2)

    print(f"Model saved to {config.MODEL_PATH} (Test ROC-AUC = {metrics['roc_auc']:.4f})")
    return metrics


if __name__ == "__main__":
    run_training_pipeline()
