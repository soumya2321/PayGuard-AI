"""
risk_engine.py - Core Multi-Vector Risk Engine implementing the 5-step UPI Fraud Detection Algorithm.

Layers:
- Input & Validation
- Derivative Calculation (amount deviation, velocity, hour, device status, location status)
- Behavioral Analysis Module
- Receiver Analysis Module
- Machine Learning Module (Placeholder -> Full Pipeline)
- Risk Engine Aggregator
- Classification (SAFE <= 30, REVIEW 31-70, HIGH RISK > 70)
- Persistence & Explainability
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Session

from app.models.schema_models import (
    User,
    BehaviorProfile,
    Transaction,
    Prediction,
    ReceiverProfile,
    FraudAlert,
    ModelVersion,
)


class RiskEngine:
    def __init__(self, ml_predictor=None):
        self.ml_predictor = ml_predictor

    def placeholder_ml_predict(self, features: Dict[str, float]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Placeholder ML inference for Step 1 until the real trained model is attached.
        Calculates a well-calibrated fraud probability from the extracted feature set.
        """
        score = 0.05  # baseline fraud rate

        amt = features.get("amount", 0.0)
        amt_dev = features.get("amount_deviation", 0.0)
        hour = features.get("hour", 12.0)
        velocity = features.get("transaction_velocity", 0.0)
        is_new_device = features.get("is_new_device", 0.0)
        is_new_location = features.get("is_new_location", 0.0)
        receiver_risk = features.get("receiver_risk_score", 20.0)

        # Feature contributions
        contributions = []

        if amt_dev > 3.0:
            score += 0.35
            contributions.append({
                "feature": "amount_deviation",
                "label": "High Amount Deviation",
                "importance": 0.35,
                "description": f"Transaction amount is {amt_dev:.1f}x higher than user historical average.",
            })
        elif amt_dev > 1.5:
            score += 0.15
            contributions.append({
                "feature": "amount_deviation",
                "label": "Moderate Amount Deviation",
                "importance": 0.15,
                "description": f"Amount departs from typical range ({amt_dev:.1f}x average).",
            })

        if velocity >= 3.0:
            score += 0.25
            contributions.append({
                "feature": "transaction_velocity",
                "label": "Rapid Transaction Velocity",
                "importance": 0.25,
                "description": f"High frequency: {int(velocity)} transactions in the past hour.",
            })

        if 0 <= hour <= 5:
            score += 0.15
            contributions.append({
                "feature": "hour",
                "label": "Unusual Transaction Hour",
                "importance": 0.15,
                "description": f"Payment initiated at {int(hour):02d}:00 (off-peak overnight window).",
            })

        if is_new_device > 0.5:
            score += 0.20
            contributions.append({
                "feature": "is_new_device",
                "label": "Unrecognized Device Fingerprint",
                "importance": 0.20,
                "description": "Payment performed from a device not seen in the user's historical profile.",
            })

        if is_new_location > 0.5:
            score += 0.15
            contributions.append({
                "feature": "is_new_location",
                "label": "Anomalous Geographic Location",
                "importance": 0.15,
                "description": "Transaction initiated outside user's primary historical locations.",
            })

        if receiver_risk > 60.0:
            score += 0.25
            contributions.append({
                "feature": "receiver_risk_score",
                "label": "Flagged / High-Risk Receiver",
                "importance": 0.25,
                "description": f"Receiver risk rating is elevated at {receiver_risk:.1f}/100.",
            })

        # Clamp probability between 0.02 and 0.98
        fraud_probability = max(0.02, min(0.98, score))

        # Sort contributions by importance
        contributions.sort(key=lambda x: x["importance"], reverse=True)
        return fraud_probability, contributions

    def evaluate_behavioral_profile(
        self, profile: Optional[BehaviorProfile], amount: float, tx_time: datetime, device: str, location: str, db: Session, user_id: int
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Behavioral Analysis Module:
        Compares current transaction against the user's historical patterns.
        """
        avg_amount = profile.avgTransactionAmount if profile else 1500.0
        primary_locations = (profile.primaryLocations if profile else "").lower()
        device_patterns = (profile.deviceUsePatterns if profile else "").lower()

        # 1. Amount deviation
        amount_deviation = abs(amount - avg_amount) / max(avg_amount, 50.0)

        # 2. Transaction velocity (count in last 60 minutes)
        window_start = tx_time - timedelta(hours=1)
        recent_count = (
            db.query(Transaction)
            .filter(Transaction.userId == user_id, Transaction.timestamp >= window_start)
            .count()
        )
        velocity = float(recent_count)

        # 3. Transaction hour
        hour = tx_time.hour
        is_unusual_hour = (0 <= hour <= 5)

        # 4. Device status
        curr_device = device.lower()
        known_devices = [d.strip() for d in device_patterns.split(",") if d.strip()]
        is_known_device = any(kd in curr_device or curr_device in kd for kd in known_devices) if known_devices else False
        is_new_device = 0.0 if is_known_device else 1.0

        # 5. Location status
        curr_loc = location.lower()
        known_locs = [l.strip() for l in primary_locations.split(";") if l.strip()]
        if not known_locs:
            known_locs = [l.strip() for l in primary_locations.split(",") if l.strip()]
        is_known_location = any(kl in curr_loc or curr_loc in kl for kl in known_locs) if known_locs else False
        is_new_location = 0.0 if is_known_location else 1.0

        # Calculate Behavioral Risk Score (0-100)
        behavioral_score = 5.0  # base
        if amount_deviation > 3.0:
            behavioral_score += 35.0
        elif amount_deviation > 1.5:
            behavioral_score += 18.0

        if velocity >= 3.0:
            behavioral_score += 25.0
        elif velocity >= 1.0:
            behavioral_score += 10.0

        if is_unusual_hour:
            behavioral_score += 15.0

        if is_new_device > 0.5:
            behavioral_score += 20.0

        if is_new_location > 0.5:
            behavioral_score += 15.0

        behavioral_risk = min(100.0, max(0.0, behavioral_score))

        derivatives = {
            "amount_deviation": amount_deviation,
            "transaction_velocity": velocity,
            "hour": float(hour),
            "is_unusual_hour": is_unusual_hour,
            "is_new_device": is_new_device,
            "is_new_location": is_new_location,
            "avg_amount": avg_amount,
        }

        return behavioral_risk, derivatives

    def evaluate_receiver_profile(self, receiver_address: str) -> Tuple[float, float]:
        """
        Receiver Analysis Module:
        Evaluates receiver reputation score (0-100, higher is better)
        and receiver risk rating (0-100, higher is riskier).
        """
        rec_lower = receiver_address.lower()

        # Suspicious markers
        suspicious_keywords = ["lottery", "prize", "cashout", "fake", "mule", "crypto", "urgent", "phish", "reward99"]
        # Trusted merchant markers
        trusted_keywords = ["fresh", "mart", "store", "supermarket", "starbucks", "hotel", "swiggy", "zomato", "amazon", "flipkart", "irctc"]

        if any(w in rec_lower for w in suspicious_keywords):
            reputation = 12.0
            risk_rating = 88.0
        elif any(w in rec_lower for w in trusted_keywords):
            reputation = 94.0
            risk_rating = 6.0
        else:
            # Standard receiver
            reputation = 75.0
            risk_rating = 25.0

        return reputation, risk_rating

    def run_pipeline(
        self,
        db: Session,
        user_id: int,
        amount: float,
        location: str,
        device_type: str,
        payment_method: str = "UPI",
        receiver_address: str = "merchant@upi",
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Executes the complete 5-step UPI Fraud Risk Detection Algorithm.
        """
        # Step 1: Input & Validation
        if amount <= 0:
            raise ValueError("Transaction amount must be strictly greater than 0.")
        if not location or not location.strip():
            raise ValueError("Location is required.")
        if not device_type or not device_type.strip():
            raise ValueError("Device type is required.")

        user = db.query(User).filter(User.userId == user_id).first()
        if not user:
            raise ValueError(f"User ID {user_id} does not exist.")

        tx_time = timestamp or datetime.utcnow()

        # Step 2: Persist initial transaction
        tx = Transaction(
            userId=user_id,
            amount=amount,
            timestamp=tx_time,
            location=location.strip(),
            deviceType=device_type.strip(),
            paymentMethod=payment_method.strip(),
            status="PROCESSING",
        )
        db.add(tx)
        db.flush()

        # Step 3: Multi-Vector Risk Analysis
        # 3a. User Behavioral Analysis
        profile = (
            db.query(BehaviorProfile)
            .filter(BehaviorProfile.userId == user_id)
            .first()
        )
        behavioral_risk, derivatives = self.evaluate_behavioral_profile(
            profile=profile,
            amount=amount,
            tx_time=tx_time,
            device=device_type,
            location=location,
            db=db,
            user_id=user_id,
        )

        # 3b. Receiver Analysis
        reputation_score, receiver_risk = self.evaluate_receiver_profile(receiver_address)
        rec_profile = ReceiverProfile(
            transactionId=tx.transactionId,
            receiverReputationScore=reputation_score,
            receiverRiskRating=receiver_risk,
            calculatedAt=tx_time,
            receiverAddress=receiver_address,
        )
        db.add(rec_profile)

        # 3c. Machine Learning Prediction
        features = {
            "amount": amount,
            "amount_deviation": derivatives["amount_deviation"],
            "hour": derivatives["hour"],
            "transaction_velocity": derivatives["transaction_velocity"],
            "is_new_device": derivatives["is_new_device"],
            "is_new_location": derivatives["is_new_location"],
            "receiver_risk_score": receiver_risk,
        }

        if self.ml_predictor and hasattr(self.ml_predictor, "predict_with_explanation"):
            ml_fraud_prob, explanations = self.ml_predictor.predict_with_explanation(features)
        else:
            ml_fraud_prob, explanations = self.placeholder_ml_predict(features)

        # 3d. Aggregate: Risk Engine Composite Score
        # Weighting: ML (50%), Behavioral Profile (30%), Receiver Profile (20%)
        composite_score = round(
            (ml_fraud_prob * 100.0 * 0.50) + (behavioral_risk * 0.30) + (receiver_risk * 0.20),
            2,
        )
        composite_score = max(0.0, min(100.0, composite_score))

        # Step 4: Classification
        # <= 30: SAFE, 31-70: REVIEW, > 70: HIGH RISK
        created_alert = None
        if composite_score <= 30.0:
            risk_level = "SAFE"
            prediction_result = "Not Fraud"
            tx_status = "COMPLETED"
        elif composite_score <= 70.0:
            risk_level = "REVIEW"
            prediction_result = "Not Fraud"
            tx_status = "FLAGGED"
        else:
            risk_level = "HIGH RISK"
            prediction_result = "Fraud"
            tx_status = "BLOCKED"

            severity = "CRITICAL" if composite_score >= 85.0 else "HIGH"
            top_cause = explanations[0]["label"] if explanations else "ANOMALY_DETECTED"
            alert_type = top_cause.upper().replace(" ", "_")

            created_alert = FraudAlert(
                transactionId=tx.transactionId,
                alertType=alert_type,
                alertSeverity=severity,
                alertTimestamp=tx_time,
                status="PENDING",
            )
            db.add(created_alert)

        # Update transaction status
        tx.status = tx_status

        # Step 5: Persist Prediction Record
        active_model = db.query(ModelVersion).order_by(ModelVersion.modelVersionId.desc()).first()
        model_version_id = active_model.modelVersionId if active_model else None

        pred = Prediction(
            transactionId=tx.transactionId,
            modelVersionId=model_version_id,
            predictionResult=prediction_result,
            fraudProbability=round(ml_fraud_prob, 4),
            riskScore=composite_score,
            predictionTimestamp=tx_time,
        )
        db.add(pred)
        db.commit()

        # Build response payload
        alert_info = None
        if created_alert:
            alert_info = {
                "alertId": created_alert.alertId,
                "transactionId": created_alert.transactionId,
                "alertType": created_alert.alertType,
                "alertSeverity": created_alert.alertSeverity,
                "alertTimestamp": created_alert.alertTimestamp.isoformat(),
                "status": created_alert.status,
            }

        # Build human-readable explanation
        summary_lines = []
        if risk_level == "SAFE":
            summary_lines.append("Transaction conforms to expected user behavior and known device/location patterns.")
        elif risk_level == "REVIEW":
            summary_lines.append("Elevated risk detected due to minor deviations in transaction context. Secondary OTP challenge recommended.")
        else:
            summary_lines.append("High fraud probability detected across telemetry vectors. Transaction halted pending investigation.")

        return {
            "transactionId": tx.transactionId,
            "userId": tx.userId,
            "userName": user.name,
            "amount": tx.amount,
            "timestamp": tx.timestamp.isoformat(),
            "location": tx.location,
            "deviceType": tx.deviceType,
            "paymentMethod": tx.paymentMethod,
            "status": tx.status,
            "prediction": {
                "predictionId": pred.predictionId,
                "predictionResult": pred.predictionResult,
                "fraudProbability": pred.fraudProbability,
                "riskScore": pred.riskScore,
                "riskLevel": risk_level,
                "modelVersionId": pred.modelVersionId,
                "predictionTimestamp": pred.predictionTimestamp.isoformat(),
            },
            "receiverProfile": {
                "receiverProfileId": rec_profile.receiverProfileId,
                "receiverAddress": rec_profile.receiverAddress,
                "receiverReputationScore": rec_profile.receiverReputationScore,
                "receiverRiskRating": rec_profile.receiverRiskRating,
            },
            "behavioralAnalysis": {
                "behavioralRiskScore": behavioral_risk,
                "amountDeviation": round(derivatives["amount_deviation"], 2),
                "transactionVelocity": derivatives["transaction_velocity"],
                "hour": derivatives["hour"],
                "isUnusualHour": derivatives["is_unusual_hour"],
                "isNewDevice": bool(derivatives["is_new_device"]),
                "isNewLocation": bool(derivatives["is_new_location"]),
                "userAvgAmount": derivatives["avg_amount"],
            },
            "alert": alert_info,
            "explanation": {
                "summary": " ".join(summary_lines),
                "contributingFactors": explanations,
            },
        }


# Singleton engine instance wired with trained XGBoost UPI Predictor
from ml.upi_predictor import upi_predictor
risk_engine = RiskEngine(ml_predictor=upi_predictor)
