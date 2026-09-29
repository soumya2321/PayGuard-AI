"""
schema_models.py - Declarative SQLAlchemy models matching the project ER diagram exactly.

Schema entities:
1. USER (userId PK, name, email, passwordHash, role, createdAt)
2. BEHAVIOR_PROFILE (profileId PK, userId FK, lastUpdate, avgTransactionAmount, avgTransactionFrequency, primaryLocations, deviceUsePatterns)
3. TRANSACTION (transactionId PK, userId FK, amount, timestamp, location, deviceType, paymentMethod, status)
4. PREDICTION (predictionId PK, transactionId FK, modelVersionId FK, predictionResult, fraudProbability, riskScore, predictionTimestamp)
5. RECEIVER_PROFILE (receiverProfileId PK, transactionId FK, receiverReputationScore, receiverRiskRating, calculatedAt, receiverAddress)
6. FRAUD_ALERT (alertId PK, transactionId FK, alertType, alertSeverity, alertTimestamp, status)
7. FEEDBACK (feedbackId PK, userId FK, transactionId FK, feedbackType, comments, feedbackTimestamp)
8. MODEL_VERSION (modelVersionId PK, modelName, deploymentDate, description, performanceMetrics)
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Date,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    userId = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    passwordHash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="USER")
    createdAt = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    behaviorProfile = relationship(
        "BehaviorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    transactions = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
    feedbacks = relationship("Feedback", back_populates="user")


class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"

    profileId = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey("users.userId", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    lastUpdate = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    avgTransactionAmount = Column(Float, nullable=False, default=1500.0)
    avgTransactionFrequency = Column(Float, nullable=False, default=3.5)  # txns / day
    primaryLocations = Column(String(255), nullable=False, default="Bengaluru, Karnataka")
    deviceUsePatterns = Column(String(255), nullable=False, default="Android, Mobile App")

    # Relationships
    user = relationship("User", back_populates="behaviorProfile")


class Transaction(Base):
    __tablename__ = "transactions"

    transactionId = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey("users.userId", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    location = Column(String(100), nullable=False)
    deviceType = Column(String(50), nullable=False)
    paymentMethod = Column(String(50), nullable=False, default="UPI")
    status = Column(String(50), nullable=False, default="PENDING")  # COMPLETED, FLAGGED, BLOCKED

    # Relationships
    user = relationship("User", back_populates="transactions")
    prediction = relationship(
        "Prediction", back_populates="transaction", uselist=False, cascade="all, delete-orphan"
    )
    receiverProfiles = relationship(
        "ReceiverProfile", back_populates="transaction", cascade="all, delete-orphan"
    )
    alerts = relationship(
        "FraudAlert", back_populates="transaction", cascade="all, delete-orphan"
    )
    feedbacks = relationship(
        "Feedback", back_populates="transaction", cascade="all, delete-orphan"
    )


class Prediction(Base):
    __tablename__ = "predictions"

    predictionId = Column(Integer, primary_key=True, autoincrement=True)
    transactionId = Column(
        Integer,
        ForeignKey("transactions.transactionId", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    modelVersionId = Column(Integer, ForeignKey("model_versions.modelVersionId"), nullable=True)
    predictionResult = Column(String(50), nullable=False)  # 'Fraud' or 'Not Fraud'
    fraudProbability = Column(Float, nullable=False)        # 0.0 - 1.0
    riskScore = Column(Float, nullable=False)               # 0.0 - 100.0
    predictionTimestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    transaction = relationship("Transaction", back_populates="prediction")
    modelVersion = relationship("ModelVersion", back_populates="predictions")


class ReceiverProfile(Base):
    __tablename__ = "receiver_profiles"

    receiverProfileId = Column(Integer, primary_key=True, autoincrement=True)
    transactionId = Column(
        Integer, ForeignKey("transactions.transactionId", ondelete="CASCADE"), nullable=False, index=True
    )
    receiverReputationScore = Column(Float, nullable=False, default=75.0)  # 0-100
    receiverRiskRating = Column(Float, nullable=False, default=25.0)        # 0-100
    calculatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    receiverAddress = Column(String(150), nullable=False)  # UPI ID / VPA

    # Relationships
    transaction = relationship("Transaction", back_populates="receiverProfiles")


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    alertId = Column(Integer, primary_key=True, autoincrement=True)
    transactionId = Column(
        Integer, ForeignKey("transactions.transactionId", ondelete="CASCADE"), nullable=False, index=True
    )
    alertType = Column(String(100), nullable=False)        # 'ANOMALY_DETECTED', 'SUSPICIOUS_RECEIVER', etc.
    alertSeverity = Column(String(50), nullable=False)     # 'HIGH', 'CRITICAL', 'MEDIUM'
    alertTimestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = Column(String(50), nullable=False, default="PENDING")  # 'PENDING', 'REVIEWED', 'RESOLVED'

    # Relationships
    transaction = relationship("Transaction", back_populates="alerts")


class Feedback(Base):
    __tablename__ = "feedbacks"

    feedbackId = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey("users.userId", ondelete="SET NULL"), nullable=True)
    transactionId = Column(
        Integer, ForeignKey("transactions.transactionId", ondelete="SET NULL"), nullable=True
    )
    feedbackType = Column(String(50), nullable=False)       # 'CONFIRMED_FRAUD', 'FALSE_POSITIVE', 'DISPUTED'
    comments = Column(Text, nullable=True)
    feedbackTimestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="feedbacks")
    transaction = relationship("Transaction", back_populates="feedbacks")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    modelVersionId = Column(Integer, primary_key=True, autoincrement=True)
    modelName = Column(String(100), nullable=False)
    deploymentDate = Column(Date, nullable=False, default=date.today)
    description = Column(Text, nullable=True)
    performanceMetrics = Column(Text, nullable=True)  # JSON-encoded string

    # Relationships
    predictions = relationship("Prediction", back_populates="modelVersion")
