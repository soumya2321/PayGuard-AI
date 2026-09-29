"""
model.py - REST endpoints for model performance metrics, feature metadata, and evaluation plots.
"""

import os
import json
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
import config
from src.features import FEATURE_METADATA
from app.schemas.analytics import ModelMetricsResponse

router = APIRouter(prefix="/model", tags=["Model Governance & Performance"])


@router.get("/metrics", response_model=ModelMetricsResponse, summary="Retrieve audited model evaluation metrics")
async def get_model_metrics():
    """
    Returns the real evaluation metrics measured on the held-out test set
    (ROC-AUC, Precision, Recall, F1, Confusion Matrix, and feature importances).
    """
    if not os.path.exists(config.METRICS_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metrics not found. Please run the training pipeline first."
        )

    with open(config.METRICS_PATH, "r") as f:
        metrics = json.load(f)

    importances = {}
    if os.path.exists(config.FEATURE_IMPORTANCE_PATH):
        with open(config.FEATURE_IMPORTANCE_PATH, "r") as f:
            importances = json.load(f)

    return {
        "model_name": metrics.get("model_name", "XGBoost Classifier"),
        "accuracy": metrics.get("accuracy", 0.0),
        "precision": metrics.get("precision", 0.0),
        "recall": metrics.get("recall", 0.0),
        "f1_score": metrics.get("f1_score", 0.0),
        "roc_auc": metrics.get("roc_auc", 0.0),
        "average_precision": metrics.get("average_precision", 0.0),
        "cv_roc_auc": metrics.get("cv_roc_auc"),
        "true_positives": metrics.get("true_positives", 0),
        "false_positives": metrics.get("false_positives", 0),
        "true_negatives": metrics.get("true_negatives", 0),
        "false_negatives": metrics.get("false_negatives", 0),
        "total_samples": metrics.get("total_samples", 0),
        "actual_fraud_count": metrics.get("actual_fraud_count", 0),
        "predicted_fraud_count": metrics.get("predicted_fraud_count", 0),
        "false_positive_rate": metrics.get("false_positive_rate", 0.0),
        "false_negative_rate": metrics.get("false_negative_rate", 0.0),
        "feature_importances": importances,
    }


@router.get("/features", summary="Retrieve feature dictionary and metadata")
async def get_feature_definitions():
    """
    Returns feature dictionary containing display labels, categories, descriptions,
    and normalized baseline ranges for each feature.
    """
    return {
        "features": FEATURE_METADATA,
        "base_feature_count": len(config.FEATURE_COLUMNS),
        "risk_thresholds": {
            "low": config.RISK_THRESHOLD_LOW,
            "high": config.RISK_THRESHOLD_HIGH,
        },
    }


@router.get("/figures/{figure_name}", summary="Retrieve evaluation plot image")
async def get_figure(figure_name: str):
    """
    Serves generated evaluation visualization plots:
    - confusion_matrix.png
    - roc_curve.png
    - precision_recall_curve.png
    - feature_importance.png
    """
    safe_name = os.path.basename(figure_name)
    if not safe_name.endswith(".png"):
        safe_name += ".png"

    path = os.path.join(config.FIGURES_DIR, safe_name)
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Figure '{safe_name}' not found."
        )

    return FileResponse(path, media_type="image/png")
