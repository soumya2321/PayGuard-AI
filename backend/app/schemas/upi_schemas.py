"""
upi_schemas.py - Pydantic models matching the 4-layer PayGuard AI architecture.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ── 1. Transaction Ingestion ──────────────────────────────────────────────────
class TransactionCreate(BaseModel):
    userId: int = Field(..., description="ID of the user making the transaction", gt=0)
    amount: float = Field(..., description="Transaction amount in INR", gt=0)
    location: str = Field(..., min_length=2, max_length=100)
    deviceType: str = Field(..., min_length=2, max_length=50)
    paymentMethod: str = Field("UPI", min_length=2, max_length=50)
    receiverAddress: Optional[str] = Field("merchant@upi", max_length=150)
    timestamp: Optional[datetime] = Field(None, description="Optional custom transaction timestamp e.g. for time-of-day simulation")


# ── 2. Risk & Prediction Details ──────────────────────────────────────────────
class ContributingFactor(BaseModel):
    feature: str
    label: str
    importance: float
    description: str


class PredictionDetail(BaseModel):
    predictionId: int
    predictionResult: str
    fraudProbability: float
    riskScore: float
    riskLevel: str
    modelVersionId: Optional[int] = None
    predictionTimestamp: str


class ReceiverProfileDetail(BaseModel):
    receiverProfileId: int
    receiverAddress: str
    receiverReputationScore: float
    receiverRiskRating: float


class BehavioralAnalysisDetail(BaseModel):
    behavioralRiskScore: float
    amountDeviation: float
    transactionVelocity: float
    hour: float
    isUnusualHour: bool
    isNewDevice: bool
    isNewLocation: bool
    userAvgAmount: float


class AlertDetail(BaseModel):
    alertId: int
    transactionId: int
    alertType: str
    alertSeverity: str
    alertTimestamp: str
    status: str


class TransactionResponse(BaseModel):
    transactionId: int
    userId: int
    userName: str
    amount: float
    timestamp: str
    location: str
    deviceType: str
    paymentMethod: str
    status: str
    prediction: PredictionDetail
    receiverProfile: ReceiverProfileDetail
    behavioralAnalysis: BehavioralAnalysisDetail
    alert: Optional[AlertDetail] = None
    explanation: Dict[str, Any]


# ── 3. Transaction History List ───────────────────────────────────────────────
class TransactionListItem(BaseModel):
    transactionId: int
    userId: int
    userName: str
    amount: float
    timestamp: str
    location: str
    deviceType: str
    paymentMethod: str
    status: str
    riskScore: float
    riskLevel: str
    fraudProbability: float
    predictionResult: str
    receiverAddress: str


class TransactionHistoryResponse(BaseModel):
    items: List[TransactionListItem]
    total: int
    limit: int
    offset: int


# ── 4. Alerts ─────────────────────────────────────────────────────────────────
class AlertListItem(BaseModel):
    alertId: int
    transactionId: int
    userId: int
    userName: str
    amount: float
    alertType: str
    alertSeverity: str
    alertTimestamp: str
    status: str
    riskScore: float
    fraudProbability: float
    location: str
    deviceType: str
    receiverAddress: str


class AlertUpdatePayload(BaseModel):
    status: str = Field(..., description="'PENDING', 'REVIEWED', or 'RESOLVED'")
    analyst_notes: Optional[str] = None


# ── 5. Dashboard Stats ────────────────────────────────────────────────────────
class DashboardStatsResponse(BaseModel):
    totalTransactions: int
    totalFraudDetected: int
    fraudRatePercentage: float
    alertsToday: int
    avgRiskScore: float
    pendingAlerts: int
    riskLevelDistribution: Dict[str, int]
    recentTransactions: List[TransactionListItem]


# ── 6. Analytics Trends ───────────────────────────────────────────────────────
class AnalyticsTrendsResponse(BaseModel):
    volumeOverTime: List[Dict[str, Any]]
    riskScoreDistribution: List[Dict[str, Any]]
    fraudByDevice: List[Dict[str, Any]]
    fraudByLocation: List[Dict[str, Any]]
    fraudByHour: List[Dict[str, Any]]


# ── 7. User Behavior Profile ──────────────────────────────────────────────────
class UserBehaviorProfileResponse(BaseModel):
    userId: int
    name: str
    email: str
    role: str
    createdAt: str
    profileId: Optional[int] = None
    avgTransactionAmount: float
    avgTransactionFrequency: float
    primaryLocations: str
    deviceUsePatterns: str
    lastUpdate: str
    totalUserTransactions: int
    flaggedUserTransactions: int
    recentUserTransactions: List[Dict[str, Any]]
