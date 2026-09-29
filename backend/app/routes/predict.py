"""
predict.py - REST endpoints for transaction fraud evaluation and simulation.
"""

from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status
from app.schemas.transaction import (
    TransactionFeatureInput,
    TransactionSimulationRequest,
    PredictionResult,
    TransactionRecord,
)
from app.services.db_service import get_db_service
from app.services.prediction_service import get_prediction_service

router = APIRouter(prefix="/predict", tags=["Fraud Prediction"])


@router.post("", response_model=PredictionResult)
async def evaluate_transaction(features: TransactionFeatureInput):
    try:
        svc = get_prediction_service()
        result = svc.predict_single(features.model_dump())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )


@router.post("/simulate", response_model=TransactionRecord)
async def simulate_transaction(payload: TransactionSimulationRequest):
    try:
        from datetime import datetime
        svc = get_prediction_service()
        db = get_db_service()

        features_dict = payload.features.model_dump()
        location = payload.location or "Bengaluru, Karnataka"
        device_type = payload.device_type or "Samsung Galaxy S23"

        # Parse time_of_day if supplied
        tx_dt = datetime.utcnow()
        if payload.time_of_day:
            try:
                t_str = payload.time_of_day.strip().upper()
                if "AM" in t_str or "PM" in t_str:
                    pt = datetime.strptime(t_str, "%I:%M %p").time()
                else:
                    pt = datetime.strptime(t_str, "%H:%M").time()
                tx_dt = tx_dt.replace(hour=pt.hour, minute=pt.minute, second=0)
            except Exception:
                pass

        # Check location discrepancy against baseline if not explicitly set
        loc_lower = location.lower()
        if "kolkata" in loc_lower or "delhi" in loc_lower or "mumbai" in loc_lower:
            if features_dict.get("geographic_disparity", 0.0) == 0.0:
                features_dict["geographic_disparity"] = 2.5
                features_dict["geographic_location_vs_ip"] = 2.0

        if "new" in device_type.lower() or "unrecognized" in device_type.lower() or "iphone" in device_type.lower():
            if features_dict.get("user_id_freq", 0.0) == 0.0:
                features_dict["user_id_freq"] = 3.5

        prediction = svc.predict_single(features_dict)

        # Mirror and execute PayGuard ER Risk Engine
        er_result = None
        try:
            from app.database import SessionLocal
            from app.models.schema_models import User
            from app.services.risk_engine import risk_engine
            with SessionLocal() as session:
                user = session.query(User).filter(User.email == payload.sender_upi_id).first()
                u_id = user.userId if user else 1
                er_result = risk_engine.run_pipeline(
                    db=session,
                    user_id=u_id,
                    amount=payload.amount_inr,
                    location=location,
                    device_type=device_type,
                    payment_method="COLLECT_REQUEST" if prediction["is_fraud"] else "UPI",
                    receiver_address=payload.receiver_upi_id,
                    timestamp=tx_dt,
                )
        except Exception as synce:
            print(f"[Sync] Non-blocking ER sync note: {synce}")

        # Determine composite results
        if er_result:
            er_pred = er_result.get("prediction", {})
            risk_lvl = er_pred.get("riskLevel", "SAFE")
            if risk_lvl == "HIGH RISK":
                final_tier = "HIGH"
                final_action = "BLOCK_OR_ESCALATE"
                is_flagged = True
            elif risk_lvl == "REVIEW":
                final_tier = "MODERATE"
                final_action = "CHALLENGE_OTP"
                is_flagged = True
            else:
                final_tier = "LOW"
                final_action = "APPROVE"
                is_flagged = False

            final_risk_score = er_pred.get("fraudProbability", prediction["fraud_probability"])
            final_rec = er_result.get("explanation", {}).get("summary", prediction["recommendation"])

            # Format factors
            top_factors = []
            for f in er_result.get("explanation", {}).get("contributingFactors", []):
                top_factors.append({
                    "feature": f.get("feature", "risk_factor"),
                    "label": f.get("label", "Signal"),
                    "category": "Behavioral / Location Context",
                    "value": float(f.get("importance", 0.5)),
                    "importance": float(f.get("importance", 0.5)),
                    "impact_score": round(float(f.get("importance", 0.5)) * 100, 1),
                    "is_risk_factor": True,
                    "description": f.get("description", ""),
                })
            if not top_factors:
                top_factors = prediction["top_risk_factors"]
        else:
            final_tier = prediction["risk_tier"]
            final_action = prediction["action"]
            is_flagged = prediction["is_fraud"]
            final_risk_score = prediction["fraud_probability"]
            final_rec = prediction["recommendation"]
            top_factors = prediction["top_risk_factors"]

        tx_id_str = f"UPI-TXN-{uuid.uuid4().hex[:8].upper()}"
        status_label = "FLAGGED" if is_flagged else "COMPLETED"

        tx_record = {
            "transaction_id": tx_id_str,
            "sender_upi": payload.sender_upi_id,
            "receiver_upi": payload.receiver_upi_id,
            "transaction_amount": payload.amount_inr,
            "transaction_type": "COLLECT_REQUEST" if is_flagged else "P2P",
            "device_id": device_type,
            "location": location,
            "ip_address": "49.36.120.15",
            "merchant_category": "PEER_TRANSFER",
            "transaction_status": status_label,
            "feature_telemetry": features_dict,
        }

        saved = db.save_transaction(tx_record, prediction)

        return {
            "id": saved["id"],
            "transaction_ref": saved["transaction_id"],
            "sender_upi_id": saved["sender_upi"],
            "receiver_upi_id": saved["receiver_upi"],
            "amount_inr": saved["transaction_amount"],
            "location": location,
            "device_type": device_type,
            "time_of_day": payload.time_of_day or tx_dt.strftime("%I:%M %p"),
            "status": saved["transaction_status"],
            "risk_score": final_risk_score,
            "risk_tier": final_tier,
            "is_fraud_predicted": final_tier == "HIGH",
            "actual_fraud_status": None,
            "recommendation": final_rec,
            "action": final_action,
            "top_risk_factors": top_factors,
            "feature_snapshot": features_dict,
            "created_at": saved["created_at"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation error: {str(e)}"
        )


@router.post("/batch", response_model=List[PredictionResult])
async def evaluate_batch(transactions: List[TransactionFeatureInput]):
    try:
        svc = get_prediction_service()
        results = svc.predict_batch([tx.model_dump() for tx in transactions])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch error: {str(e)}"
        )
