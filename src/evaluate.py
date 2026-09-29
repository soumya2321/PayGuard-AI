"""
evaluate.py - Evaluation metrics, visualization generation, and reporting for UPI Fraud Detection.
"""

from typing import Dict, Any, List, Optional
import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    average_precision_score,
    confusion_matrix,
    classification_report,
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def compute_metrics(y_true: pd.Series, y_pred: np.ndarray, y_prob: Optional[np.ndarray] = None) -> Dict[str, Any]:
    """
    Compute comprehensive classification metrics.
    """
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics: Dict[str, Any] = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "total_samples": int(len(y_true)),
        "actual_fraud_count": int(sum(y_true)),
        "predicted_fraud_count": int(sum(y_pred)),
        "false_positive_rate": round(float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0, 4),
        "false_negative_rate": round(float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0, 4),
    }

    if y_prob is not None:
        metrics["roc_auc"] = round(float(roc_auc_score(y_true, y_prob)), 4)
        metrics["average_precision"] = round(float(average_precision_score(y_true, y_prob)), 4)

    return metrics


def print_classification_summary(y_true: pd.Series, y_pred: np.ndarray) -> None:
    """Print standard classification report."""
    print("\n--- Detailed Classification Report ---")
    print(classification_report(y_true, y_pred, target_names=["Legitimate", "Fraud"]))


def plot_confusion_matrix(y_true: pd.Series, y_pred: np.ndarray, save_path: Optional[str] = None) -> None:
    """Generate and save styled Confusion Matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Legitimate (0)", "Fraud (1)"],
        yticklabels=["Legitimate (0)", "Fraud (1)"],
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")
    plt.title("Confusion Matrix - UPI Fraud Detection")
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200)
        print(f"Confusion matrix saved to {save_path}")
    plt.close()


def plot_roc_curve(y_true: pd.Series, y_prob: np.ndarray, save_path: Optional[str] = None) -> None:
    """Generate and save ROC Curve."""
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auc = roc_auc_score(y_true, y_prob)

    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, color="#2563eb", lw=2.5, label=f"Model ROC (AUC = {auc:.4f})")
    plt.plot([0, 1], [0, 1], color="#94a3b8", lw=1.5, linestyle="--", label="Random Baseline (AUC = 0.50)")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate (Recall)")
    plt.title("ROC Curve - UPI Fraud Detection")
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200)
        print(f"ROC curve saved to {save_path}")
    plt.close()


def plot_precision_recall_curve(y_true: pd.Series, y_prob: np.ndarray, save_path: Optional[str] = None) -> None:
    """Generate and save Precision-Recall Curve."""
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    avg_prec = average_precision_score(y_true, y_prob)

    plt.figure(figsize=(7, 5))
    plt.plot(recall, precision, color="#10b981", lw=2.5, label=f"PR Curve (AP = {avg_prec:.4f})")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve (Imbalanced Fraud Detection)")
    plt.legend(loc="lower left")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200)
        print(f"Precision-Recall curve saved to {save_path}")
    plt.close()


def plot_feature_importance(
    importances: Dict[str, float],
    top_n: int = 15,
    save_path: Optional[str] = None,
) -> None:
    """Plot horizontal bar chart of top feature importances."""
    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:top_n]
    features = [item[0] for item in sorted_items]
    scores = [item[1] for item in sorted_items]

    plt.figure(figsize=(9, 6))
    y_pos = np.arange(len(features))
    plt.barh(y_pos, scores, align="center", color="#6366f1")
    plt.yticks(y_pos, features)
    plt.gca().invert_yaxis()  # Highest at top
    plt.xlabel("Normalized Importance")
    plt.title(f"Top {top_n} Features Driving UPI Fraud Detection")
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200)
        print(f"Feature importance plot saved to {save_path}")
    plt.close()


def run_full_evaluation(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    feature_names: List[str],
) -> Dict[str, Any]:
    """
    Run full model evaluation, print summaries, and persist all artifacts & plots.
    """
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = compute_metrics(y_test, y_pred, y_prob)
    print("\n================ EVALUATION METRICS ================")
    for k, v in metrics.items():
        print(f"  {k:25s}: {v}")
    print("====================================================")

    print_classification_summary(y_test, y_pred)

    # Persist figures
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    plot_confusion_matrix(y_test, y_pred, save_path=os.path.join(config.FIGURES_DIR, "confusion_matrix.png"))
    plot_roc_curve(y_test, y_prob, save_path=os.path.join(config.FIGURES_DIR, "roc_curve.png"))
    plot_precision_recall_curve(y_test, y_prob, save_path=os.path.join(config.FIGURES_DIR, "precision_recall_curve.png"))

    # Extract & save feature importances
    feature_importance_dict: Dict[str, float] = {}
    if hasattr(model, "feature_importances_"):
        raw_importances = model.feature_importances_
        feature_importance_dict = {
            feat: round(float(imp), 5) for feat, imp in zip(feature_names, raw_importances)
        }
        plot_feature_importance(
            feature_importance_dict,
            top_n=15,
            save_path=os.path.join(config.FIGURES_DIR, "feature_importance.png"),
        )

        with open(config.FEATURE_IMPORTANCE_PATH, "w") as f:
            json.dump(feature_importance_dict, f, indent=2)

    # Persist metrics json
    with open(config.METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    # Also save to reports
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    with open(os.path.join(config.REPORTS_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    return metrics
