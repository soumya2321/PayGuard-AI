"""
analytics.py - Pydantic schemas for dashboard statistics and model performance.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_transactions: int
    fraud_count: int
    legitimate_count: int
    fraud_rate_percentage: float
    average_risk_score: float
    total_volume_inr: float
    fraud_volume_inr: float
    pending_critical_alerts: int
    database_mode: str


class TierDistributionItem(BaseModel):
    name: str
    value: int
    color: str


class TimeTrendItem(BaseModel):
    date: str
    total: int
    flagged: int
    legitimate: int
    avg_risk: float


class RiskFactorCount(BaseModel):
    factor: str
    count: int


class DashboardAnalyticsResponse(BaseModel):
    summary: AnalyticsSummary
    tier_distribution: List[TierDistributionItem]
    time_trend: List[TimeTrendItem]
    top_risk_factors: List[RiskFactorCount]


class ModelMetricsResponse(BaseModel):
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    average_precision: float
    cv_roc_auc: Optional[float] = None
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    total_samples: int
    actual_fraud_count: int
    predicted_fraud_count: int
    false_positive_rate: float
    false_negative_rate: float
    feature_importances: Dict[str, float]
