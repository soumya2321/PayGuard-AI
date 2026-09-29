"""
predict.py - Real-time inference engine and risk assessment for UPI Fraud Detection.
Evaluates incoming UPI transactions, calculates calibrated risk probabilities,
and identifies key behavioral risk drivers.
"""

from typing import Dict, Any, List, Union
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.features import add_behavioral_features, explain_prediction, FEATURE_METADATA


class FraudPredictionService:
    """
    Thread-safe prediction service with caching of model and preprocessing artifacts.
    """
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.feature_importances = {}
        self.metrics = {}
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load persisted models, scalers, and schemas."""
        if not os.path.exists(config.MODEL_PATH):
            raise FileNotFoundError(
                f"Trained model not found at {config.MODEL_PATH}. Run src/train.py first."
            )
        if not os.path.exists(config.SCALER_PATH):
            raise FileNotFoundError(
                f"Feature scaler not found at {config.SCALER_PATH}. Run src/train.py first."
            )

        self.model = joblib.load(config.MODEL_PATH)
        self.scaler = joblib.load(config.SCALER_PATH)

        if os.path.exists(config.FEATURES_PATH):
            with open(config.FEATURES_PATH, "r") as f:
                self.feature_columns = json.load(f)
        else:
            self.feature_columns = config.FEATURE_COLUMNS

        if os.path.exists(config.FEATURE_IMPORTANCE_PATH):
            with open(config.FEATURE_IMPORTANCE_PATH, "r") as f:
                self.feature_importances = json.load(f)

        if os.path.exists(config.METRICS_PATH):
            with open(config.METRICS_PATH, "r") as f:
                self.metrics = json.load(f)

    def _determine_risk_tier(self, probability: float) -> Dict[str, str]:
        """
        Map probability to calibrated risk tier and recommended operational action.
        """
        if probability >= config.RISK_THRESHOLD_HIGH:
            return {
                "risk_tier": "HIGH",
                "risk_level": "High Risk",
                "color_code": "red",
                "recommendation": "Block transaction immediately or require biometric step-up verification.",
                "action": "BLOCK_OR_ESCALATE",
            }
        elif probability >= config.RISK_THRESHOLD_LOW:
            return {
                "risk_tier": "MODERATE",
                "risk_level": "Moderate Risk",
                "color_code": "amber",
                "recommendation": "Prompt user with warning banner and require 2-step OTP confirmation.",
                "action": "CHALLENGE_OTP",
            }
        else:
            return {
                "risk_tier": "LOW",
                "risk_level": "Low Risk",
                "color_code": "green",
                "recommendation": "Transaction appears consistent with legitimate behavioral patterns. Fast-track approval.",
                "action": "APPROVE",
            }

    def predict_single(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run inference and risk decomposition on a single transaction payload.
        """
        # Ensure all base features exist, default to 0.0
        row: Dict[str, float] = {}
        for col in config.FEATURE_COLUMNS:
            raw_val = transaction.get(col, 0.0)
            try:
                row[col] = float(raw_val)
            except (ValueError, TypeError):
                row[col] = 0.0

        # Construct single-row DataFrame
        df_raw = pd.DataFrame([row])

        # Apply standard scaler to raw feature subset
        scaled_array = self.scaler.transform(df_raw[config.FEATURE_COLUMNS])
        df_scaled = pd.DataFrame(scaled_array, columns=config.FEATURE_COLUMNS)

        # Apply behavioral feature engineering
        df_engineered = add_behavioral_features(df_scaled)

        # Align with model expected features
        if self.feature_columns:
            for col in self.feature_columns:
                if col not in df_engineered.columns:
                    df_engineered[col] = 0.0
            df_model_input = df_engineered[self.feature_columns]
        else:
            df_model_input = df_engineered

        # Predict probability
        prob = float(self.model.predict_proba(df_model_input)[0, 1])
        prediction_label = int(prob >= 0.5)

        tier_info = self._determine_risk_tier(prob)

        # Generate top contributing risk factors
        row_features = df_model_input.iloc[0].to_dict()
        top_risk_factors = explain_prediction(
            row_features,
            self.feature_importances,
            top_k=5,
        )

        return {
            "prediction": prediction_label,
            "is_fraud": bool(prediction_label == 1),
            "fraud_probability": round(prob, 4),
            "risk_score_percentage": round(prob * 100, 1),
            "risk_tier": tier_info["risk_tier"],
            "risk_level": tier_info["risk_level"],
            "color_code": tier_info["color_code"],
            "recommendation": tier_info["recommendation"],
            "action": tier_info["action"],
            "top_risk_factors": top_risk_factors,
            "disclaimer": (
                "Educational Fraud-Risk Detection System: This prediction represents an estimated "
                "risk likelihood calculated from behavioral and contextual patterns. It is intended "
                "as a decision-support indicator, not as an absolute guarantee of fraud or legitimacy."
            ),
        }

    def predict_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run batch inference for multiple transactions.
        """
        return [self.predict_single(tx) for tx in transactions]


# Global singleton instance
_service = None

def get_prediction_service() -> FraudPredictionService:
    global _service
    if _service is None:
        _service = FraudPredictionService()
    return _service


def predict_single(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function for quick single predictions."""
    service = get_prediction_service()
    return service.predict_single(transaction)


def predict_batch(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Helper function for batch predictions."""
    service = get_prediction_service()
    return service.predict_batch(transactions)


if __name__ == "__main__":
    svc = get_prediction_service()
    sample = {col: 0.0 for col in config.FEATURE_COLUMNS}
    sample["amount"] = 5.2
    sample["geographic_disparity"] = 2.5
    res = svc.predict_single(sample)
    print("Sample prediction test:")
    print(json.dumps(res, indent=2))
