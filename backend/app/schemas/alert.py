"""
alert.py - Pydantic schemas for fraud alerts.
"""

from typing import Optional
from pydantic import BaseModel, Field


class AlertUpdate(BaseModel):
    status: str = Field(..., pattern="^(PENDING|REVIEWED|CONFIRMED_FRAUD|FALSE_POSITIVE)$")
    analyst_notes: Optional[str] = Field(None, max_length=1000)


class AlertRecord(BaseModel):
    id: str
    transaction_id: str
    transaction_ref: str
    severity: str
    risk_score: float
    alert_title: str
    description: str
    status: str
    analyst_notes: Optional[str] = None
    reviewed_at: Optional[str] = None
    created_at: str
