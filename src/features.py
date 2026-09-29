"""
features.py - Feature engineering and metadata for UPI Fraud Detection.
Adds domain-informed behavioral, temporal, and interaction features.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd

# ── Feature Metadata Dictionary ──────────────────────────────────────────────
FEATURE_METADATA: Dict[str, Dict[str, Any]] = {
    "amount": {
        "label": "Transaction Amount",
        "category": "Financial",
        "description": "Standardized value of the transfer amount.",
        "min": -2.0, "max": 8.0, "default": 0.0,
    },
    "session_duration": {
        "label": "Session Duration",
        "category": "Session & Timing",
        "description": "Total active time of the user in the UPI app before initiating payment.",
        "min": -2.0, "max": 5.0, "default": 0.0,
    },
    "receiver_transaction_history": {
        "label": "Receiver Trust Score",
        "category": "Financial",
        "description": "Historical legitimate transaction score of the recipient VPA/account.",
        "min": -3.0, "max": 2.0, "default": 0.0,
    },
    "transaction_amount_vs_sender_history": {
        "label": "Amount Deviation vs History",
        "category": "Financial",
        "description": "Ratio/deviation between current amount and sender's usual 30-day average.",
        "min": -1.0, "max": 25.0, "default": 0.0,
    },
    "geographic_disparity": {
        "label": "Geographic Disparity",
        "category": "Network & Location",
        "description": "Physical distance discrepancy between usual location and current GPS coordinate.",
        "min": -1.0, "max": 3.0, "default": 0.0,
    },
    "transaction_time_of_day": {
        "label": "Time of Day (Cyclical)",
        "category": "Session & Timing",
        "description": "Standardized cyclical timestamp indicator for unusual hour payments.",
        "min": -2.0, "max": 2.0, "default": 0.0,
    },
    "time_between_link_click_and_transaction": {
        "label": "Click-to-Pay Delay",
        "category": "Biometric & Input",
        "description": "Time elapsed between clicking an external link/SMS and confirming the payment.",
        "min": -1.0, "max": 10.0, "default": 0.0,
    },
    "input_timing_consistency": {
        "label": "Input Timing Consistency",
        "category": "Biometric & Input",
        "description": "Rhythm consistency of keystrokes during UPI PIN and form entry.",
        "min": -3.0, "max": 2.0, "default": 0.0,
    },
    "keyboard_input_speed": {
        "label": "Keyboard Entry Speed",
        "category": "Biometric & Input",
        "description": "Keystroke entry speed; abnormally high speeds may indicate bot automation.",
        "min": -3.0, "max": 2.0, "default": 0.0,
    },
    "input_pause_patterns": {
        "label": "Input Hesitation Pauses",
        "category": "Biometric & Input",
        "description": "Number of unusual micro-pauses while entering PIN or recipient details.",
        "min": -1.0, "max": 7.0, "default": 0.0,
    },
    "screen_active_time": {
        "label": "Screen Active Duration",
        "category": "Session & Timing",
        "description": "How long the screen remained on prior to confirming payment.",
        "min": -2.0, "max": 4.0, "default": 0.0,
    },
    "geographic_location_vs_ip": {
        "label": "GPS vs IP Discrepancy",
        "category": "Network & Location",
        "description": "Mismatch score between device GPS coordinates and cellular/WiFi ISP location.",
        "min": -1.0, "max": 3.0, "default": 0.0,
    },
    "background_data_usage": {
        "label": "Background Data Activity",
        "category": "Network & Location",
        "description": "Suspicious high background network traffic (remote-access tools or malware).",
        "min": -1.0, "max": 7.0, "default": 0.0,
    },
    "pin_entry_speed": {
        "label": "UPI PIN Entry Velocity",
        "category": "Biometric & Input",
        "description": "Speed of entering the 4 or 6-digit MPIN.",
        "min": -3.0, "max": 2.0, "default": 0.0,
    },
    "request_amount_roundness": {
        "label": "Round Amount Indicator",
        "category": "Financial",
        "description": "Tendency of the requested transaction to be round figures (e.g. ₹5,000, ₹10,000).",
        "min": -1.0, "max": 15.0, "default": 0.0,
    },
    "request_acceptance_rate": {
        "label": "Collect Request Acceptance Rate",
        "category": "Financial",
        "description": "Historical rate of approving incoming UPI collect payment requests.",
        "min": -1.0, "max": 9.0, "default": 0.0,
    },
    "time_to_respond_to_request": {
        "label": "Response Time to Collect Request",
        "category": "Session & Timing",
        "description": "Time taken from receiving collect notification to approval.",
        "min": -1.0, "max": 10.0, "default": 0.0,
    },
    "user_id_freq": {
        "label": "Device / User Frequency",
        "category": "Session & Timing",
        "description": "Transaction velocity and frequency associated with this user ID / device.",
        "min": -1.0, "max": 6.0, "default": 0.0,
    },
}


def add_behavioral_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create interaction, ratio, and anomaly features from raw columns.
    """
    df = df.copy()

    # 1. Speed-timing interaction: fast input with long pause is suspicious (coached user or bot)
    if "keyboard_input_speed" in df.columns and "input_pause_patterns" in df.columns:
        df["speed_pause_interaction"] = (df["keyboard_input_speed"] * df["input_pause_patterns"]).clip(-20.0, 20.0)

    # 2. Combined geographic risk: GPS mismatch + IP mismatch
    if "geographic_disparity" in df.columns and "geographic_location_vs_ip" in df.columns:
        df["geo_risk_score"] = (df["geographic_disparity"] + df["geographic_location_vs_ip"]).clip(-10.0, 10.0)

    # 3. Amount anomaly: amount scaled by historical sender deviation
    if "amount" in df.columns and "transaction_amount_vs_sender_history" in df.columns:
        df["amount_anomaly"] = (df["amount"] * df["transaction_amount_vs_sender_history"]).clip(-50.0, 50.0)

    # 4. Session velocity: amount transferred relative to session duration
    if "amount" in df.columns and "session_duration" in df.columns:
        safe_duration = df["session_duration"].apply(lambda v: v if abs(v) > 0.05 else np.nan)
        df["amount_per_session"] = (df["amount"] / safe_duration).fillna(0.0).clip(-20.0, 20.0)

    # 5. Fast response flag: rapid approvals often correlate with social engineering or scripted exploits
    if "time_to_respond_to_request" in df.columns:
        df["is_fast_response"] = (df["time_to_respond_to_request"] < -0.8).astype(float)

    # 6. Round amount flag: round amounts occur significantly more frequently in scam requests
    if "request_amount_roundness" in df.columns:
        df["is_round_amount"] = (df["request_amount_roundness"] > 0.5).astype(float)

    # 7. Device / Network anomaly: high background data combined with location disparity
    if "background_data_usage" in df.columns and "geographic_location_vs_ip" in df.columns:
        df["device_network_risk"] = (df["background_data_usage"] * (df["geographic_location_vs_ip"] + 1.0)).clip(-20.0, 20.0)

    # 8. Input anomaly index: inconsistent timing combined with abnormal PIN speed
    if "input_timing_consistency" in df.columns and "pin_entry_speed" in df.columns:
        df["input_irregularity"] = (df["pin_entry_speed"] - df["input_timing_consistency"]).clip(-10.0, 10.0)

    return df


def get_all_feature_names(df: pd.DataFrame) -> List[str]:
    """Return the list of all column names after feature engineering."""
    transformed = add_behavioral_features(df.head(2))
    return list(transformed.columns)


def explain_prediction(
    transaction_features: Dict[str, float],
    feature_importances: Dict[str, float],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Generate intuitive risk factor explanations for a single transaction.
    Combines feature value deviation with global feature importance.
    """
    contributions = []

    for feature_name, value in transaction_features.items():
        importance = feature_importances.get(feature_name, 0.01)
        meta = FEATURE_METADATA.get(feature_name, {
            "label": feature_name.replace("_", " ").title(),
            "category": "Behavioral",
            "description": "Engineered behavioral factor.",
        })

        # Higher values typically represent higher deviations/risk in standard scaling
        impact_score = float(value * importance)

        contributions.append({
            "feature": feature_name,
            "label": meta["label"],
            "category": meta["category"],
            "value": round(float(value), 3),
            "importance": round(float(importance), 4),
            "impact_score": round(impact_score, 4),
            "is_risk_factor": impact_score > 0.05,
            "description": meta.get("description", ""),
        })

    # Sort descending by absolute impact
    contributions.sort(key=lambda x: abs(x["impact_score"]), reverse=True)
    return contributions[:top_k]
