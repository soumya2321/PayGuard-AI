"""
evaluate.py - Comprehensive evaluation metrics, comparative reporting,
and diagnostic visualization generation for UPI Fraud Detection models.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Headless non-interactive plotting
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    classification_report,
)

ML_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ML_DIR.parent
ARTIFACTS_DIR = ML_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def compute_comprehensive_metrics(
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """
    Computes all standard classification metrics:
    Accuracy, Precision, Recall, F1-Score, ROC-AUC, and Confusion Matrix breakdown.
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

    return metrics


def plot_confusion_matrix(
    y_true: pd.Series,
    y_pred: np.ndarray,
    model_name: str,
    save_path: Optional[Path] = None,
) -> None:
    """
    Plots and saves a styled Confusion Matrix heatmap.
    """
    if save_path is None:
        save_path = ARTIFACTS_DIR / "confusion_matrix.png"

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Legitimate (0)", "Fraud (1)"],
        yticklabels=["Legitimate (0)", "Fraud (1)"],
        cbar=False,
    )
    plt.xlabel("Predicted Label", fontweight="bold")
    plt.ylabel("Actual Label", fontweight="bold")
    plt.title(f"Confusion Matrix — {model_name}", pad=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[Evaluation] Confusion matrix saved to {save_path}")


def plot_comparative_roc_curves(
    models_dict: Dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    save_path: Optional[Path] = None,
) -> None:
    """
    Plots ROC curves for all candidate models on a single comparison chart.
    """
    if save_path is None:
        save_path = ARTIFACTS_DIR / "roc_curves.png"

    plt.figure(figsize=(8, 6))

    colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"]

    for i, (name, model) in enumerate(models_dict.items()):
        try:
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)[:, 1]
            elif hasattr(model, "decision_function"):
                y_prob = model.decision_function(X_test)
            else:
                continue

            fpr, tpr, _ = roc_curve(y_test, y_prob)
            auc_score = roc_auc_score(y_test, y_prob)
            plt.plot(fpr, tpr, color=colors[i % len(colors)], lw=2.2, label=f"{name} (AUC = {auc_score:.4f})")
        except Exception as e:
            print(f"Skipping ROC curve for {name}: {e}")

    plt.plot([0, 1], [0, 1], color="#94a3b8", lw=1.5, linestyle="--", label="Random Chance (AUC = 0.50)")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate", fontweight="bold")
    plt.ylabel("True Positive Rate (Recall)", fontweight="bold")
    plt.title("Comparative ROC Curves — All Candidate Models", pad=12)
    plt.legend(loc="lower right", frameon=True)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[Evaluation] Comparative ROC curves saved to {save_path}")


def plot_feature_importance(
    model: Any,
    feature_names: List[str],
    save_path: Optional[Path] = None,
    top_n: int = 15,
) -> Dict[str, float]:
    """
    Extracts, plots, and saves feature importances (or coefficients).
    """
    importances_dict: Dict[str, float] = {}

    if hasattr(model, "feature_importances_"):
        raw_importances = model.feature_importances_
        importances_dict = {
            feat: round(float(imp), 5) for feat, imp in zip(feature_names, raw_importances)
        }
    elif hasattr(model, "coef_"):
        raw_coefs = np.abs(model.coef_[0])
        total = np.sum(raw_coefs) if np.sum(raw_coefs) > 0 else 1.0
        importances_dict = {
            feat: round(float(c / total), 5) for feat, c in zip(feature_names, raw_coefs)
        }
    else:
        return {}

    # Save JSON
    json_path = ARTIFACTS_DIR / "feature_importance.json"
    with open(json_path, "w") as f:
        json.dump(importances_dict, f, indent=2)

    # Plot Bar Chart
    if save_path is None:
        save_path = ARTIFACTS_DIR / "feature_importance.png"

    sorted_items = sorted(importances_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
    feats = [item[0] for item in sorted_items]
    scores = [item[1] for item in sorted_items]

    plt.figure(figsize=(9, 6))
    y_pos = np.arange(len(feats))
    plt.barh(y_pos, scores, align="center", color="#4f46e5")
    plt.yticks(y_pos, feats)
    plt.gca().invert_yaxis()
    plt.xlabel("Importance Weight", fontweight="bold")
    plt.title(f"Top {top_n} Behavioral Features Driving Fraud Risk", pad=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[Evaluation] Feature importance chart saved to {save_path}")

    return importances_dict


def save_evaluation_report(
    comparison_results: Dict[str, Dict[str, Any]],
    champion_name: str,
    save_path: Optional[Path] = None,
) -> None:
    """
    Serializes comprehensive model comparison report to JSON and Markdown.
    """
    if save_path is None:
        save_path = ARTIFACTS_DIR / "model_evaluation_report.json"

    report = {
        "champion_model": champion_name,
        "champion_metrics": comparison_results[champion_name],
        "candidate_models": comparison_results,
        "selection_rationale": (
            "Model selected based on highest ROC-AUC and F1-score on held-out test data. "
            "In imbalanced fraud detection, high Recall minimizes costly undetected frauds "
            "(False Negatives), while high Precision limits operational false alarms (False Positives)."
        ),
    }

    with open(save_path, "w") as f:
        json.dump(report, f, indent=2)

    # Also save comparison summary table JSON
    with open(ARTIFACTS_DIR / "model_comparison.json", "w") as f:
        json.dump(comparison_results, f, indent=2)

    print(f"[Evaluation] Evaluation report saved to {save_path}")
