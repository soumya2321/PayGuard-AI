"""
predict.py - Real-time inference module for the UPI Fraud Detection ML pipeline.
Loads serialized preprocessor, champion model, and feature schemas.
Provides single-transaction and batch prediction with explainability.
"""

from typing import Dict, Any, List, Union, Optional
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from ml.preprocessing import (
    BASE_FEATURE_COLUMNS,
    engineer_features,
    detect_and_clean_invalid_values,
    handle_missing_values,
    ARTIFACTS_DIR,
    PROJECT_ROOT,
)

# Fallback paths
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = ARTIFACTS_DIR / "final_model.joblib"
if not MODEL_PATH.exists():
    MODEL_PATH = MODELS_DIR / "model.pkl"

PREPROCESSOR_PATH = ARTIFACTS_DIR / "preprocessor.joblib"
if not PREPROCESSOR_PATH.exists():
    PREPROCESSOR_PATH = MODELS_DIR / "scaler.pkl"

FEATURE_NAMES_PATH = ARTIFACTS_DIR / "feature_names.json"
if not FEATURE_NAMES_PATH.exists():
    FEATURE_NAMES_PATH = MODELS_DIR / "features.json"

FEATURE_IMPORTANCE_PATH = ARTIFACTS_DIR / "feature_importance.json"
if not FEATURE_IMPORTANCE_PATH.exists():
    FEATURE_IMPORTANCE_PATH = MODELS_DIR / "feature_importance.json"


class UPIFraudPredictor:
    """
    Production-ready inference engine for UPI transaction fraud detection.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        preprocessor_path: Optional[Path] = None,
        feature_names_path: Optional[Path] = None,
    ):
        self.model_path = Path(model_path) if model_path else MODEL_PATH
        self.preprocessor_path = Path(preprocessor_path) if preprocessor_path else PREPROCESSOR_PATH
        self.feature_names_path = Path(feature_names_path) if feature_names_path else FEATURE_NAMES_PATH

        self.model = None
        self.scaler = None
        self.feature_names: List[str] = []
        self.feature_importances: Dict[str, float] = {}

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Loads serialized model, scaler, and feature schemas."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Trained model not found at {self.model_path}. Please execute `python ml/train.py` first."
            )
        self.model = joblib.load(self.model_path)

        if not self.preprocessor_path.exists():
            raise FileNotFoundError(
                f"Fitted scaler not found at {self.preprocessor_path}. Please execute `python ml/train.py` first."
            )
        self.scaler = joblib.load(self.preprocessor_path)

        if self.feature_names_path.exists():
            with open(self.feature_names_path, "r", encoding="utf-8") as f:
                self.feature_names = json.load(f)
        else:
            self.feature_names = BASE_FEATURE_COLUMNS

        if FEATURE_IMPORTANCE_PATH.exists():
            try:
                with open(FEATURE_IMPORTANCE_PATH, "r", encoding="utf-8") as f:
                    self.feature_importances = json.load(f)
            except Exception:
                self.feature_importances = {}

    def _prepare_features(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms raw transaction features into the engineered feature matrix.
        """
        # Ensure all base features exist
        for col in BASE_FEATURE_COLUMNS:
            if col not in df_raw.columns:
                df_raw[col] = 0.0

        # Retain base columns in designated order
        df_base = df_raw[BASE_FEATURE_COLUMNS].copy()

        # Handle missing values & outliers
        df_base = handle_missing_values(df_base)
        df_base = detect_and_clean_invalid_values(df_base)

        # Scale base numerical features using the fitted preprocessor
        scaled_array = self.scaler.transform(df_base)
        df_scaled = pd.DataFrame(scaled_array, columns=BASE_FEATURE_COLUMNS, index=df_base.index)

        # Apply domain behavioral feature engineering
        df_engineered = engineer_features(df_scaled)

        # Align with final trained feature columns
        for col in self.feature_names:
            if col not in df_engineered.columns:
                df_engineered[col] = 0.0

        return df_engineered[self.feature_names]

    def _classify_risk_tier(self, probability: float) -> str:
        """Classifies probability into standard risk tiers."""
        if probability >= 0.70:
            return "HIGH"
        elif probability >= 0.35:
            return "MODERATE"
        return "LOW"

    def _extract_top_risk_factors(
        self,
        row_dict: Dict[str, float],
        top_k: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Identifies key features contributing to the risk score.
        """
        explanations = []
        for feature, val in row_dict.items():
            importance = self.feature_importances.get(feature, 0.05)
            # Higher absolute value combined with positive weight indicates risk anomaly
            anomaly_score = abs(float(val)) * (1.0 + importance)
            explanations.append({
                "feature": feature,
                "value": round(float(val), 4),
                "anomaly_score": round(anomaly_score, 4),
                "importance_weight": round(importance, 4),
            })

        # Sort descending by anomaly score
        explanations.sort(key=lambda x: x["anomaly_score"], reverse=True)
        return explanations[:top_k]

    def predict(self, transaction: Union[Dict[str, Any], pd.DataFrame]) -> Dict[str, Any]:
        """
        Predicts fraud likelihood for a single transaction or dictionary payload.
        """
        if isinstance(transaction, dict):
            df_raw = pd.DataFrame([{col: float(transaction.get(col, 0.0)) for col in BASE_FEATURE_COLUMNS}])
        elif isinstance(transaction, pd.DataFrame):
            df_raw = transaction.copy()
        else:
            raise TypeError("Transaction input must be a dictionary or pandas DataFrame.")

        df_input = self._prepare_features(df_raw)

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(df_input)
            fraud_prob = float(probabilities[0, 1])
        else:
            fraud_prob = float(self.model.predict(df_input)[0])

        is_fraud = bool(fraud_prob >= 0.50)
        risk_level = self._classify_risk_tier(fraud_prob)
        top_factors = self._extract_top_risk_factors(df_input.iloc[0].to_dict())

        return {
            "prediction": 1 if is_fraud else 0,
            "is_fraud": is_fraud,
            "fraud_probability": round(fraud_prob, 4),
            "risk_score": round(fraud_prob * 100, 1),
            "risk_level": risk_level,
            "top_risk_factors": top_factors,
            "model_version": getattr(self.model, "__class__", type(self.model)).__name__,
            "disclaimer": (
                "Educational Decision Support: Probabilistic risk indication "
                "based on behavioral telemetry and historical transaction patterns."
            ),
        }

    def predict_batch(self, df_transactions: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Batch prediction for a dataframe of multiple transactions.
        """
        df_input = self._prepare_features(df_transactions)
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(df_input)[:, 1]
        else:
            probs = self.model.predict(df_input)

        results = []
        for i, prob in enumerate(probs):
            p = float(prob)
            results.append({
                "index": i,
                "prediction": 1 if p >= 0.50 else 0,
                "is_fraud": p >= 0.50,
                "fraud_probability": round(p, 4),
                "risk_score": round(p * 100, 1),
                "risk_level": self._classify_risk_tier(p),
            })
        return results


def run_test_inference():
    """Validates predictor with legitimate and fraudulent transaction scenarios."""
    print("\n" + "=" * 65)
    print("   RUNNING REAL-TIME INFERENCE VERIFICATION")
    print("=" * 65)

    predictor = UPIFraudPredictor()

    # Scenario 1: Typical Legitimate Transaction (low amount, normal timing, trusted receiver)
    legit_tx = {
        "amount": -0.85,
        "session_duration": 0.12,
        "receiver_transaction_history": 1.45,
        "transaction_amount_vs_sender_history": -0.42,
        "geographic_disparity": -0.55,
        "transaction_time_of_day": 0.25,
        "time_between_link_click_and_transaction": 0.0,
        "input_timing_consistency": 0.88,
        "keyboard_input_speed": 0.20,
        "input_pause_patterns": -0.30,
        "screen_active_time": 0.40,
        "geographic_location_vs_ip": -0.60,
        "background_data_usage": -0.45,
        "pin_entry_speed": 0.15,
        "request_amount_roundness": -0.20,
        "request_acceptance_rate": 0.95,
        "time_to_respond_to_request": 0.35,
        "user_id_freq": 1.10,
    }

    # Scenario 2: Suspicious / Fraudulent Transaction (huge amount deviation, IP discrepancy, rapid forced approval)
    fraud_tx = {
        "amount": 4.50,
        "session_duration": -1.20,
        "receiver_transaction_history": -2.10,
        "transaction_amount_vs_sender_history": 7.80,
        "geographic_disparity": 2.85,
        "transaction_time_of_day": -1.80,
        "time_between_link_click_and_transaction": 4.50,
        "input_timing_consistency": -2.30,
        "keyboard_input_speed": -1.90,
        "input_pause_patterns": 4.10,
        "screen_active_time": -1.40,
        "geographic_location_vs_ip": 2.90,
        "background_data_usage": 3.40,
        "pin_entry_speed": -2.10,
        "request_amount_roundness": 3.80,
        "request_acceptance_rate": -1.50,
        "time_to_respond_to_request": -1.25,
        "user_id_freq": -1.80,
    }

    print("\n--- Evaluating Legitimate Transaction ---")
    res_legit = predictor.predict(legit_tx)
    print(f"Prediction: {res_legit['prediction']} (is_fraud={res_legit['is_fraud']})")
    print(f"Risk Score: {res_legit['risk_score']}% ({res_legit['risk_level']})")
    print(f"Fraud Probability: {res_legit['fraud_probability']}")

    print("\n--- Evaluating Fraudulent Transaction ---")
    res_fraud = predictor.predict(fraud_tx)
    print(f"Prediction: {res_fraud['prediction']} (is_fraud={res_fraud['is_fraud']})")
    print(f"Risk Score: {res_fraud['risk_score']}% ({res_fraud['risk_level']})")
    print(f"Fraud Probability: {res_fraud['fraud_probability']}")
    print("Top Risk Factors:")
    for f in res_fraud["top_risk_factors"]:
        print(f"  - {f['feature']}: val={f['value']}, anomaly_score={f['anomaly_score']}")

    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_test_inference()
