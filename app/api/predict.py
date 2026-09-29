"""
predict.py - REST endpoints for real-time fraud prediction and transaction simulation.
"""

from typing import List, Dict, Any
import uuid
from fastapi import APIRouter, HTTPException, status
from app.schemas.transaction import (
    TransactionFeatureInput,
    TransactionSimulationRequest,
    PredictionResult,
    TransactionRecord,
)
from app.services.db_service import get_db_service
from src.predict import get_prediction_service

router = APIRouter(prefix="/predict", tags=["Fraud Prediction Engine"])


@router.post("", response_model=PredictionResult, summary="Evaluate transaction risk score without database persistence")
async def evaluate_transaction(features: TransactionFeatureInput):
    """
    Score transaction telemetry features through the machine learning model.
    Returns calibrated fraud probability, risk category, actionable recommendations,
    top contributing behavioral factors, and educational disclaimers.
    """
    try:
        svc = get_prediction_service()
        result = svc.predict_single(features.model_dump())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )


@router.post("/simulate", response_model=TransactionRecord, summary="Simulate an end-to-end UPI payment with database persistence")
async def simulate_transaction(payload: TransactionSimulationRequest):
    """
    Simulates a live UPI payment transfer:
    1. Evaluates behavioral and transactional features through the ML model.
    2. Calculates calibrated risk score and tier (Low, Moderate, High).
    3. Persists the transaction audit log to Supabase PostgreSQL (or local SQLite fallback).
    4. Automatically creates a high-priority Fraud Alert if risk tier is elevated.
    """
    try:
        svc = get_prediction_service()
        db = get_db_service()

        features_dict = payload.features.model_dump()
        prediction = svc.predict_single(features_dict)

        tx_ref = f"UPI-{uuid.uuid4().hex[:8].upper()}"
        status_label = "FLAGGED" if prediction["is_fraud"] else "COMPLETED"

        tx_record = {
            "transaction_ref": tx_ref,
            "sender_upi_id": payload.sender_upi_id,
            "receiver_upi_id": payload.receiver_upi_id,
            "amount_inr": payload.amount_inr,
            "status": status_label,
            "risk_score": prediction["fraud_probability"],
            "risk_tier": prediction["risk_tier"],
            "is_fraud_predicted": prediction["is_fraud"],
            "actual_fraud_status": None,
            "recommendation": prediction["recommendation"],
            "action": prediction["action"],
            "top_risk_factors": prediction["top_risk_factors"],
            "feature_snapshot": features_dict,
        }

        saved = db.save_transaction(tx_record)
        return saved
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation error: {str(e)}"
        )


@router.post("/batch", response_model=List[PredictionResult], summary="Run batch fraud risk evaluations")
async def evaluate_batch(transactions: List[TransactionFeatureInput]):
    """
    Scores multiple transactions concurrently.
    """
    try:
        svc = get_prediction_service()
        results = svc.predict_batch([tx.model_dump() for tx in transactions])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch inference error: {str(e)}"
        )
