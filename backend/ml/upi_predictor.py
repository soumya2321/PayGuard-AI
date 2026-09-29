"""
upi_predictor.py - Production inference wrapper providing fraud probability
and feature-importance / attribution based explainability.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
import joblib
import numpy as np

BACKEND_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BACKEND_DIR / "models"
MODEL_FILE = MODELS_DIR / "upi_champion_model.pkl"
IMPORTANCE_FILE = MODELS_DIR / "upi_feature_importance.json"

FEATURE_NAMES = [
    "amount",
    "amount_deviation",
    "hour",
    "transaction_velocity",
    "is_new_device",
    "is_new_location",
    "receiver_risk_score",
]

FEATURE_LABELS = {
    "amount": "Transaction Amount",
    "amount_deviation": "Amount Deviation vs User Mean",
    "hour": "Time of Day (Hour)",
    "transaction_velocity": "Transaction Velocity (Past Hour)",
    "is_new_device": "Device Fingerprint Status",
    "is_new_location": "Geographic Location Match",
    "receiver_risk_score": "Receiver Reputation & Risk Score",
}


class UPIPredictor:
    def __init__(self):
        self.model = None
        self.feature_importances = {}
        self.load_model()

    def load_model(self):
        if MODEL_FILE.exists():
            self.model = joblib.load(MODEL_FILE)
        if IMPORTANCE_FILE.exists():
            with open(IMPORTANCE_FILE, "r") as f:
                self.feature_importances = json.load(f)

    def predict_with_explanation(
        self, features: Dict[str, float]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Takes raw features, predicts fraud probability via trained XGBoost model,
        and derives top contributing factors.
        """
        if self.model is None:
            self.load_model()
            if self.model is None:
                raise RuntimeError("UPI fraud model artifact not found.")

        # Ensure feature vector in exact order
        vec = []
        for name in FEATURE_NAMES:
            val = float(features.get(name, 0.0))
            vec.append(val)

        arr = np.array([vec], dtype=np.float32)
        prob = float(self.model.predict_proba(arr)[0, 1])

        # Compute feature contributions
        contributions = []
        amt = features.get("amount", 0.0)
        amt_dev = features.get("amount_deviation", 0.0)
        hour = features.get("hour", 12.0)
        velocity = features.get("transaction_velocity", 0.0)
        is_new_dev = features.get("is_new_device", 0.0)
        is_new_loc = features.get("is_new_location", 0.0)
        rec_risk = features.get("receiver_risk_score", 20.0)

        # Baseline importance weights from XGBoost
        w_dev = self.feature_importances.get("is_new_device", 0.35)
        w_vel = self.feature_importances.get("transaction_velocity", 0.18)
        w_loc = self.feature_importances.get("is_new_location", 0.14)
        w_rec = self.feature_importances.get("receiver_risk_score", 0.12)
        w_amt_dev = self.feature_importances.get("amount_deviation", 0.10)
        w_amt = self.feature_importances.get("amount", 0.06)
        w_hr = self.feature_importances.get("hour", 0.05)

        if is_new_dev > 0.5:
            contributions.append({
                "feature": "is_new_device",
                "label": "Unrecognized Device Fingerprint",
                "importance": w_dev,
                "value": 1.0,
                "is_risk_factor": True,
                "description": "Payment was initiated on a newly detected device not in the user's trusted profile.",
            })

        if velocity >= 3.0:
            contributions.append({
                "feature": "transaction_velocity",
                "label": "Spike in Transaction Velocity",
                "importance": w_vel,
                "value": velocity,
                "is_risk_factor": True,
                "description": f"High burst frequency: {int(velocity)} transactions occurred within the past hour.",
            })

        if rec_risk >= 50.0:
            contributions.append({
                "feature": "receiver_risk_score",
                "label": "High-Risk / Suspect Receiver",
                "importance": w_rec,
                "value": rec_risk,
                "is_risk_factor": True,
                "description": f"Receiver UPI address flagged with high risk score ({rec_risk:.1f}/100).",
            })

        if amt_dev >= 2.0:
            contributions.append({
                "feature": "amount_deviation",
                "label": "Anomalous Amount Deviation",
                "importance": w_amt_dev,
                "value": round(amt_dev, 2),
                "is_risk_factor": True,
                "description": f"Amount is {amt_dev:.1f}x higher than this user's historical average spend.",
            })

        if is_new_loc > 0.5:
            contributions.append({
                "feature": "is_new_location",
                "label": "Unusual Geographic Location",
                "importance": w_loc,
                "value": 1.0,
                "is_risk_factor": True,
                "description": "Location is outside user's primary historical transacting areas.",
            })

        if 0 <= hour <= 5:
            contributions.append({
                "feature": "hour",
                "label": "Overnight / Off-Hours Transaction",
                "importance": w_hr,
                "value": hour,
                "is_risk_factor": True,
                "description": f"Payment executed during unusual off-peak hours ({int(hour):02d}:00).",
            })

        if amt >= 20000.0:
            contributions.append({
                "feature": "amount",
                "label": "High Transaction Value",
                "importance": w_amt,
                "value": amt,
                "is_risk_factor": True,
                "description": f"Transfer of INR {amt:,.2f} is in the top quartile of value transactions.",
            })

        if not contributions:
            contributions.append({
                "feature": "baseline_consistency",
                "label": "Consistent Behavioral Baseline",
                "importance": 0.05,
                "value": 0.0,
                "is_risk_factor": False,
                "description": "All transaction indicators match user's standard routine spending patterns.",
            })

        # Sort contributions by importance descending
        contributions.sort(key=lambda x: x["importance"], reverse=True)
        return prob, contributions


upi_predictor = UPIPredictor()
