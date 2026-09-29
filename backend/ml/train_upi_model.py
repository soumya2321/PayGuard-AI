"""
train_upi_model.py - Generates synthetic UPI transaction dataset with 7 domain features,
trains an XGBoost / Random Forest classifier with SMOTE / class weighting,
evaluates metrics, computes feature importances, and persists artifacts.

Features:
1. amount (INR)
2. amount_deviation (ratio vs user mean)
3. hour (0 - 23)
4. transaction_velocity (txns in recent window)
5. is_new_device (0 or 1)
6. is_new_location (0 or 1)
7. receiver_risk_score (0 - 100)
"""

import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    average_precision_score,
    confusion_matrix,
)
from xgboost import XGBClassifier

# Base paths
ML_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ML_DIR.parent
MODELS_DIR = BACKEND_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODELS_DIR / "upi_champion_model.pkl"
METRICS_FILE = MODELS_DIR / "upi_metrics.json"
FEATURES_FILE = MODELS_DIR / "upi_features.json"
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


def generate_synthetic_upi_dataset(n_samples: int = 20000, random_state: int = 42) -> pd.DataFrame:
    """
    Generates realistic synthetic UPI transaction data modeling real-world fraud vectors:
    - Account Takeover: new device + high velocity + night hours + high deviation
    - Collect Request Scam: high deviation + mule/high-risk receiver + rounded amount
    - Phishing: new location + unexpected receiver + high velocity
    - Legitimate activity: daytime, trusted receiver, low deviation, recognized device/location
    """
    np.random.seed(random_state)

    # 1. Base distributions
    # Amounts: log-normal with common UPI merchant/p2p spends
    amount = np.exp(np.random.normal(loc=6.8, scale=1.4, size=n_samples))
    amount = np.clip(amount, 10.0, 100000.0)

    # Amount deviation vs normal user mean: gamma distribution
    amount_deviation = np.random.gamma(shape=1.2, scale=1.0, size=n_samples)

    # Transaction hour: peaked between 9am and 10pm, lower overnight
    hour_probs = np.array([
        0.01, 0.008, 0.006, 0.006, 0.01, 0.02, # 00-05
        0.03, 0.05, 0.07, 0.08, 0.08, 0.07,    # 06-11
        0.06, 0.06, 0.06, 0.06, 0.07, 0.08,    # 12-17
        0.09, 0.08, 0.06, 0.04, 0.02, 0.01     # 18-23
    ])
    hour_probs /= hour_probs.sum()
    hour = np.random.choice(np.arange(24), size=n_samples, p=hour_probs)

    # Transaction velocity (recent txns in window): Poisson distribution
    transaction_velocity = np.random.poisson(lam=1.2, size=n_samples)

    # New device: Bernoulli (12% overall)
    is_new_device = np.random.binomial(n=1, p=0.12, size=n_samples)

    # New location: Bernoulli (15% overall)
    is_new_location = np.random.binomial(n=1, p=0.15, size=n_samples)

    # Receiver risk score (0 - 100): Beta skewed towards low risk (~25)
    receiver_risk_score = np.random.beta(a=2, b=6, size=n_samples) * 100.0

    # 2. Compute Fraud Latent Probability with non-linear interaction terms
    logits = (
        -4.6  # baseline intercept (~4% base fraud rate)
        + 0.55 * np.log1p(amount_deviation)
        + 0.035 * receiver_risk_score
        + 0.40 * transaction_velocity
        + 1.30 * is_new_device
        + 0.90 * is_new_location
        # Non-linear interaction anomalies:
        + 1.80 * (is_new_device * (hour < 5))               # ATO at night
        + 1.60 * ((amount_deviation > 3.0) * is_new_device)  # Large spike on new phone
        + 1.50 * ((receiver_risk_score > 60.0) * (amount > 15000)) # High value transfer to risky VPA
        + 1.20 * ((transaction_velocity >= 4) * (amount_deviation > 2.0)) # Rapid drain
    )

    probs = 1.0 / (1.0 + np.exp(-logits))
    # Generate binary label with probabilistic sampling
    is_fraud = (np.random.rand(n_samples) < probs).astype(int)

    df = pd.DataFrame({
        "amount": np.round(amount, 2),
        "amount_deviation": np.round(amount_deviation, 3),
        "hour": hour.astype(int),
        "transaction_velocity": transaction_velocity.astype(int),
        "is_new_device": is_new_device.astype(int),
        "is_new_location": is_new_location.astype(int),
        "receiver_risk_score": np.round(receiver_risk_score, 2),
        "is_fraud": is_fraud,
    })

    return df


def train_and_export():
    print("[ML Pipeline] Generating synthetic UPI dataset (20,000 transactions)...")
    df = generate_synthetic_upi_dataset(n_samples=20000, random_state=42)

    fraud_count = int(df["is_fraud"].sum())
    total_count = len(df)
    fraud_pct = (fraud_count / total_count) * 100.0
    print(f"[ML Pipeline] Dataset generated: {total_count} rows, {fraud_count} frauds ({fraud_pct:.2f}% fraud rate).")

    X = df[FEATURE_NAMES]
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Calculate class weighting for imbalance
    neg_count = int((y_train == 0).sum())
    pos_count = int((y_train == 1).sum())
    scale_pos = neg_count / max(1, pos_count)

    print(f"[ML Pipeline] Training XGBoost Classifier with scale_pos_weight={scale_pos:.2f}...")
    model = XGBClassifier(
        n_estimators=180,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=scale_pos,
        random_state=42,
        eval_metric="logloss",
    )

    model.fit(X_train, y_train)

    # Evaluate on held-out test set
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    pr_auc = float(average_precision_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = [int(v) for v in cm.ravel()]

    metrics = {
        "model_name": "XGBoost UPI Fraud Classifier",
        "algorithm": "Extreme Gradient Boosting",
        "features": FEATURE_NAMES,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "confusion_matrix": {
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp,
        },
        "test_sample_count": len(y_test),
        "training_sample_count": len(y_train),
    }

    print("\n--- MODEL PERFORMANCE ON HELD-OUT TEST DATA ---")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"PR-AUC:    {pr_auc:.4f}")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"F1-Score:  {f1:.4f}")
    print(f"Accuracy:  {acc * 100:.2f}%")

    # Feature importances
    importances = model.feature_importances_
    feat_imp = {name: round(float(imp), 4) for name, imp in zip(FEATURE_NAMES, importances)}
    # Sort descending
    feat_imp = dict(sorted(feat_imp.items(), key=lambda item: item[1], reverse=True))

    print("\n--- FEATURE IMPORTANCES ---")
    for feat, imp in feat_imp.items():
        print(f"  {feat:25s}: {imp:.4f}")

    # Persist artifacts
    joblib.dump(model, MODEL_FILE)
    print(f"\n[Artifact] Saved model to {MODEL_FILE}")

    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[Artifact] Saved metrics to {METRICS_FILE}")

    with open(FEATURES_FILE, "w") as f:
        json.dump(FEATURE_NAMES, f, indent=2)
    print(f"[Artifact] Saved feature list to {FEATURES_FILE}")

    with open(IMPORTANCE_FILE, "w") as f:
        json.dump(feat_imp, f, indent=2)
    print(f"[Artifact] Saved feature importance to {IMPORTANCE_FILE}")

    return metrics


if __name__ == "__main__":
    train_and_export()
