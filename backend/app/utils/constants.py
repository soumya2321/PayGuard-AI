"""
constants.py - Application constants, risk tiers, and operational messages.
"""

# Risk Tier Definitions
TIER_LOW = "LOW"
TIER_MODERATE = "MODERATE"
TIER_HIGH = "HIGH"

# Actions
ACTION_APPROVE = "APPROVE"
ACTION_CHALLENGE = "CHALLENGE_OTP"
ACTION_BLOCK = "BLOCK_OR_ESCALATE"

# Alert Statuses
ALERT_PENDING = "PENDING"
ALERT_REVIEWED = "REVIEWED"
ALERT_CONFIRMED = "CONFIRMED_FRAUD"
ALERT_FALSE_POSITIVE = "FALSE_POSITIVE"

# Educational Disclaimer
EDUCATIONAL_DISCLAIMER = (
    "Educational Fraud-Risk Detection System: Predictions represent probabilistic "
    "risk indications derived from behavioral telemetry and historical patterns. "
    "This system serves as an educational decision-support mechanism, not an absolute guarantee."
)
