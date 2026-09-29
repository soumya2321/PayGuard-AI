"""
predict.py - Standalone inference helper in ml module.
"""

from typing import Dict, Any, List
from pathlib import Path
import sys
import json
import joblib
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from ml.features import add_behavioral_features, explain_prediction


def run_single_inference(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """Inference helper function."""
    model = joblib.load(config.MODEL_PATH)
    scaler = joblib.load(config.SCALER_PATH)

    with open(config.FEATURES_PATH, "r") as f:
        feature_columns = json.load(f)

    with open(config.FEATURE_IMPORTANCE_PATH, "r") as f:
        feature_importances = json.load(f)

    row = {col: float(transaction.get(col, 0.0)) for col in config.FEATURE_COLUMNS}
    df_raw = pd.DataFrame([row])
    scaled = scaler.transform(df_raw[config.FEATURE_COLUMNS])
    df_scaled = pd.DataFrame(scaled, columns=config.FEATURE_COLUMNS)
    df_eng = add_behavioral_features(df_scaled)

    for col in feature_columns:
        if col not in df_eng.columns:
            df_eng[col] = 0.0
    df_input = df_eng[feature_columns]

    prob = float(model.predict_proba(df_input)[0, 1])
    is_fraud = prob >= 0.5

    top_factors = explain_prediction(df_input.iloc[0].to_dict(), feature_importances, top_k=5)

    return {
        "prediction": int(is_fraud),
        "is_fraud": is_fraud,
        "fraud_probability": round(prob, 4),
        "top_risk_factors": top_factors,
    }
