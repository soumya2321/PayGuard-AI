"""
prediction_service.py - Production inference service managing model state and calibrations.
"""

from typing import Dict, Any, List
from pathlib import Path
import sys
import json
import joblib
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import config
from ml.features import add_behavioral_features, explain_prediction, FEATURE_METADATA
from app.utils.constants import (
    TIER_LOW, TIER_MODERATE, TIER_HIGH,
    ACTION_APPROVE, ACTION_CHALLENGE, ACTION_BLOCK,
    EDUCATIONAL_DISCLAIMER
)


class PredictionService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = []
        self.feature_importances = {}
        self.metrics = {}
        self.load_artifacts()

    def load_artifacts(self) -> None:
        """Load artifacts from ml/artifacts or models directory."""
        project_root = Path(getattr(config, "PROJECT_ROOT", getattr(config, "BASE_DIR", ".")))

        ml_model_path = project_root / "ml" / "artifacts" / "final_model.joblib"
        model_path = ml_model_path if ml_model_path.exists() else Path(config.MODEL_PATH)
        if model_path.exists():
            self.model = joblib.load(model_path)

        ml_scaler_path = project_root / "ml" / "artifacts" / "preprocessor.joblib"
        scaler_path = ml_scaler_path if ml_scaler_path.exists() else Path(config.SCALER_PATH)
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)

        ml_features_path = project_root / "ml" / "artifacts" / "feature_names.json"
        features_path = ml_features_path if ml_features_path.exists() else Path(config.FEATURES_PATH)
        if features_path.exists():
            with open(features_path, "r", encoding="utf-8") as f:
                self.feature_columns = json.load(f)

        ml_importance_path = project_root / "ml" / "artifacts" / "feature_importance.json"
        importance_path = ml_importance_path if ml_importance_path.exists() else Path(config.FEATURE_IMPORTANCE_PATH)
        if importance_path.exists():
            with open(importance_path, "r", encoding="utf-8") as f:
                self.feature_importances = json.load(f)

        ml_metrics_path = project_root / "ml" / "artifacts" / "model_evaluation_report.json"
        metrics_path = Path(config.METRICS_PATH) if Path(config.METRICS_PATH).exists() else ml_metrics_path
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)

    def _determine_tier(self, prob: float) -> Dict[str, str]:
        if prob >= config.RISK_THRESHOLD_HIGH:
            return {
                "risk_tier": TIER_HIGH,
                "risk_level": "High Risk",
                "color_code": "red",
                "recommendation": "Block transaction immediately or require biometric step-up verification.",
                "action": ACTION_BLOCK,
            }
        elif prob >= config.RISK_THRESHOLD_LOW:
            return {
                "risk_tier": TIER_MODERATE,
                "risk_level": "Moderate Risk",
                "color_code": "amber",
                "recommendation": "Prompt user with warning banner and require 2-step OTP confirmation.",
                "action": ACTION_CHALLENGE,
            }
        else:
            return {
                "risk_tier": TIER_LOW,
                "risk_level": "Low Risk",
                "color_code": "green",
                "recommendation": "Transaction appears consistent with legitimate behavioral patterns. Fast-track approval.",
                "action": ACTION_APPROVE,
            }

    def predict_single(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Perform end-to-end inference and feature attribution on a transaction."""
        if self.model is None or self.scaler is None:
            self.load_artifacts()
            if self.model is None or self.scaler is None:
                raise RuntimeError("Model or Scaler artifact missing. Please run model training.")

        row = {}
        for col in config.FEATURE_COLUMNS:
            try:
                row[col] = float(transaction.get(col, 0.0))
            except (ValueError, TypeError):
                row[col] = 0.0

        df_raw = pd.DataFrame([row])
        scaled_array = self.scaler.transform(df_raw[config.FEATURE_COLUMNS])
        df_scaled = pd.DataFrame(scaled_array, columns=config.FEATURE_COLUMNS)
        df_engineered = add_behavioral_features(df_scaled)

        if self.feature_columns:
            for col in self.feature_columns:
                if col not in df_engineered.columns:
                    df_engineered[col] = 0.0
            df_input = df_engineered[self.feature_columns]
        else:
            df_input = df_engineered

        prob = float(self.model.predict_proba(df_input)[0, 1])
        is_fraud = prob >= 0.5
        tier_info = self._determine_tier(prob)

        top_factors = explain_prediction(df_input.iloc[0].to_dict(), self.feature_importances, top_k=5)

        return {
            "prediction": int(is_fraud),
            "is_fraud": is_fraud,
            "fraud_probability": round(prob, 4),
            "risk_score_percentage": round(prob * 100, 1),
            "risk_tier": tier_info["risk_tier"],
            "risk_level": tier_info["risk_level"],
            "color_code": tier_info["color_code"],
            "recommendation": tier_info["recommendation"],
            "action": tier_info["action"],
            "top_risk_factors": top_factors,
            "disclaimer": EDUCATIONAL_DISCLAIMER,
        }

    def predict_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.predict_single(tx) for tx in transactions]


_service_instance = None

def get_prediction_service() -> PredictionService:
    global _service_instance
    if _service_instance is None:
        _service_instance = PredictionService()
    return _service_instance
