"""
transaction.py - Pydantic schemas for transactions, simulation, and risk assessment.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TransactionFeatureInput(BaseModel):
    """
    Standardized numerical features representing UPI transaction & device telemetry.
    """
    amount: float = Field(0.0, description="Scaled amount of the transaction")
    session_duration: float = Field(0.0, description="Active session duration before payment")
    receiver_transaction_history: float = Field(0.0, description="Receiver trust score")
    transaction_amount_vs_sender_history: float = Field(0.0, description="Deviation from sender typical transfer size")
    geographic_disparity: float = Field(0.0, description="Physical location distance mismatch")
    transaction_time_of_day: float = Field(0.0, description="Cyclical hour of day indicator")
    time_between_link_click_and_transaction: float = Field(0.0, description="Delay between link click and payment")
    input_timing_consistency: float = Field(0.0, description="Keystroke rhythm regularity")
    keyboard_input_speed: float = Field(0.0, description="Keyboard speed score")
    input_pause_patterns: float = Field(0.0, description="Unusual hesitation pauses")
    screen_active_time: float = Field(0.0, description="Screen active time prior to confirmation")
    geographic_location_vs_ip: float = Field(0.0, description="GPS vs ISP location discrepancy")
    background_data_usage: float = Field(0.0, description="Background telemetry / data usage score")
    pin_entry_speed: float = Field(0.0, description="PIN input speed score")
    request_amount_roundness: float = Field(0.0, description="Rounded amount request metric")
    request_acceptance_rate: float = Field(0.0, description="Receiver request acceptance rate")
    time_to_respond_to_request: float = Field(0.0, description="Response delay to collect request")
    user_id_freq: float = Field(0.0, description="User / device ID transaction frequency")


class TransactionSimulationRequest(BaseModel):
    """
    Payload for simulating an end-to-end UPI payment through the fraud risk engine.
    """
    sender_upi_id: str = Field(..., min_length=3, max_length=128, example="rahul.verma@oksbi")
    receiver_upi_id: str = Field(..., min_length=3, max_length=128, example="store.merchant@paytm")
    amount_inr: float = Field(..., gt=0, example=4500.0)
    features: TransactionFeatureInput = Field(default_factory=TransactionFeatureInput)


class RiskFactorExplanation(BaseModel):
    feature: str
    label: str
    category: str
    value: float
    importance: float
    impact_score: float
    is_risk_factor: bool
    description: str


class PredictionResult(BaseModel):
    prediction: int = Field(..., description="0 for Legitimate, 1 for Suspected Fraud")
    is_fraud: bool
    fraud_probability: float = Field(..., ge=0.0, le=1.0)
    risk_score_percentage: float = Field(..., ge=0.0, le=100.0)
    risk_tier: str = Field(..., description="LOW, MODERATE, or HIGH")
    risk_level: str = Field(..., description="Human friendly risk label")
    color_code: str = Field(..., description="green, amber, or red")
    recommendation: str
    action: str = Field(..., description="APPROVE, CHALLENGE_OTP, or BLOCK_OR_ESCALATE")
    top_risk_factors: List[RiskFactorExplanation]
    disclaimer: str


class TransactionRecord(BaseModel):
    id: str
    transaction_ref: str
    sender_upi_id: str
    receiver_upi_id: str
    amount_inr: float
    status: str
    risk_score: float
    risk_tier: str
    is_fraud_predicted: bool
    actual_fraud_status: Optional[bool] = None
    recommendation: str
    action: str
    top_risk_factors: List[Dict[str, Any]]
    feature_snapshot: Dict[str, Any]
    created_at: str


class TransactionListResponse(BaseModel):
    items: List[TransactionRecord]
    total: int
    limit: int
    offset: int
