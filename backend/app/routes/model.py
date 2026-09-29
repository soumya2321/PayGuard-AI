"""
model.py - REST endpoints for model metrics, feature metadata, and plots.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
import config
from ml.features import FEATURE_METADATA
from app.schemas.analytics import ModelMetricsResponse

router = APIRouter(prefix="/model", tags=["Model Governance"])


@router.get("/metrics", response_model=ModelMetricsResponse)
async def get_model_metrics():
    metrics_path = config.METRICS_PATH
    if not metrics_path.exists():
        metrics_path = config.PROJECT_ROOT / "ml" / "artifacts" / "model_evaluation_report.json"
    if not metrics_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model metrics not found.")

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # In case model_evaluation_report structure has champion details
    if "champion_metrics" in metrics:
        champion_name = metrics.get("champion_model", "Gradient Boosting")
        metrics = metrics["champion_metrics"]
        metrics["model_name"] = champion_name

    importances = {}
    imp_path = config.FEATURE_IMPORTANCE_PATH
    if not imp_path.exists():
        imp_path = config.PROJECT_ROOT / "ml" / "artifacts" / "feature_importance.json"
    if imp_path.exists():
        with open(imp_path, "r", encoding="utf-8") as f:
            importances = json.load(f)

    return {
        "model_name": metrics.get("model_name", "Gradient Boosting"),
        "accuracy": metrics.get("accuracy", 0.0),
        "precision": metrics.get("precision", 0.0),
        "recall": metrics.get("recall", 0.0),
        "f1_score": metrics.get("f1_score", 0.0),
        "roc_auc": metrics.get("roc_auc", 0.0),
        "average_precision": metrics.get("average_precision", metrics.get("f1_score", 0.0)),
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


@router.get("/features")
async def get_feature_definitions():
    return {
        "features": FEATURE_METADATA,
        "base_feature_count": len(config.FEATURE_COLUMNS),
        "risk_thresholds": {
            "low": config.RISK_THRESHOLD_LOW,
            "high": config.RISK_THRESHOLD_HIGH,
        },
    }


@router.get("/figures/{figure_name}")
async def get_figure(figure_name: str):
    safe_name = Path(figure_name).name
    if not safe_name.endswith(".png"):
        safe_name += ".png"

    path = config.FIGURES_DIR / safe_name
    if not path.exists():
        path = config.PROJECT_ROOT / "ml" / "artifacts" / safe_name

    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Figure '{safe_name}' not found.")

    return FileResponse(str(path), media_type="image/png")
