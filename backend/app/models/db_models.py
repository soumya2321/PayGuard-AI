"""
db_models.py - Internal data structures representing Supabase database entities.
Supports: users, transactions, fraud_predictions, model_metrics.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class UserEntity:
    id: str
    full_name: str
    primary_upi_id: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    risk_segment: str = "STANDARD"
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class TransactionEntity:
    id: str
    transaction_id: str
    transaction_amount: float
    transaction_type: str
    sender_upi: str
    receiver_upi: str
    transaction_timestamp: str
    device_id: str
    location: str
    ip_address: str
    merchant_category: str
    transaction_status: str
    created_at: str
    user_id: Optional[str] = None
    feature_telemetry: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FraudPredictionEntity:
    id: str
    transaction_id: str
    prediction: int  # 0: Legitimate, 1: Suspected Fraud
    fraud_probability: float
    model_version: str
    created_at: str
    risk_tier: str = "LOW"
    recommendation: str = "Approve"
    top_risk_factors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ModelMetricEntity:
    id: str
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    created_at: str
