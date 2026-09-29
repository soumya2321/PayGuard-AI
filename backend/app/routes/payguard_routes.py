"""
payguard_routes.py - Core REST and WebSocket endpoints for PayGuard AI.

Endpoints:
- POST /transactions
- GET /transactions
- GET /transactions/{id}
- GET /alerts
- PATCH /alerts/{id}
- GET /dashboard/stats
- GET /analytics/trends
- GET /users/{id}/profile
- GET /users
- WebSocket /ws/monitor
"""

import asyncio
from datetime import datetime, timedelta
import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db, SessionLocal
from app.models.schema_models import (
    User,
    BehaviorProfile,
    Transaction,
    Prediction,
    ReceiverProfile,
    FraudAlert,
    ModelVersion,
)
from app.schemas.upi_schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionHistoryResponse,
    TransactionListItem,
    AlertListItem,
    AlertUpdatePayload,
    DashboardStatsResponse,
    AnalyticsTrendsResponse,
    UserBehaviorProfileResponse,
)
from app.services.risk_engine import risk_engine

router = APIRouter(tags=["PayGuard Core API"])


# Helper: determine risk level string from score
def get_risk_level(score: float) -> str:
    if score <= 30.0:
        return "SAFE"
    elif score <= 70.0:
        return "REVIEW"
    return "HIGH RISK"


# ── 1. POST /transactions ─────────────────────────────────────────────────────
@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    """
    Executes the full 5-step UPI Fraud Risk Detection Algorithm:
    1. Input validation & integrity check
    2. Persist transaction, extract features, calculate derivatives
    3. Multi-vector risk analysis (Behavioral, Receiver, ML)
    4. Classification (SAFE, REVIEW, HIGH RISK)
    5. Persist prediction & alerts, return detailed risk assessment
    """
    try:
        result = risk_engine.run_pipeline(
            db=db,
            user_id=payload.userId,
            amount=payload.amount,
            location=payload.location,
            device_type=payload.deviceType,
            payment_method=payload.paymentMethod,
            receiver_address=payload.receiverAddress or "merchant@upi",
            timestamp=payload.timestamp,
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction processing error: {str(e)}",
        )


# ── 2. GET /transactions ──────────────────────────────────────────────────────
@router.get("/transactions", response_model=TransactionHistoryResponse)
def list_transactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    risk_level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Transaction, User, Prediction, ReceiverProfile)
        .join(User, Transaction.userId == User.userId)
        .outerjoin(Prediction, Transaction.transactionId == Prediction.transactionId)
        .outerjoin(ReceiverProfile, Transaction.transactionId == ReceiverProfile.transactionId)
    )

    if risk_level and risk_level.upper() != "ALL":
        rl = risk_level.upper()
        if rl == "SAFE":
            query = query.filter(Prediction.riskScore <= 30.0)
        elif rl == "REVIEW":
            query = query.filter(Prediction.riskScore > 30.0, Prediction.riskScore <= 70.0)
        elif rl in ["HIGH", "HIGH RISK", "HIGH_RISK"]:
            query = query.filter(Prediction.riskScore > 70.0)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (Transaction.location.ilike(term))
            | (Transaction.deviceType.ilike(term))
            | (User.name.ilike(term))
            | (ReceiverProfile.receiverAddress.ilike(term))
        )

    total = query.count()
    rows = query.order_by(Transaction.timestamp.desc()).offset(offset).limit(limit).all()

    items = []
    for tx, usr, pred, rec in rows:
        r_score = pred.riskScore if pred else 0.0
        r_level = get_risk_level(r_score)
        items.append(
            TransactionListItem(
                transactionId=tx.transactionId,
                userId=usr.userId,
                userName=usr.name,
                amount=tx.amount,
                timestamp=tx.timestamp.isoformat(),
                location=tx.location,
                deviceType=tx.deviceType,
                paymentMethod=tx.paymentMethod,
                status=tx.status,
                riskScore=r_score,
                riskLevel=r_level,
                fraudProbability=pred.fraudProbability if pred else 0.0,
                predictionResult=pred.predictionResult if pred else "Not Fraud",
                receiverAddress=rec.receiverAddress if rec else "N/A",
            )
        )

    return TransactionHistoryResponse(items=items, total=total, limit=limit, offset=offset)


# ── 3. GET /transactions/{id} ─────────────────────────────────────────────────
@router.get("/transactions/{tx_id}")
def get_transaction_detail(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.transactionId == tx_id).first()
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction #{tx_id} not found.",
        )

    user = db.query(User).filter(User.userId == tx.userId).first()
    profile = db.query(BehaviorProfile).filter(BehaviorProfile.userId == tx.userId).first()
    pred = db.query(Prediction).filter(Prediction.transactionId == tx.transactionId).first()
    rec = db.query(ReceiverProfile).filter(ReceiverProfile.transactionId == tx.transactionId).first()
    alerts = db.query(FraudAlert).filter(FraudAlert.transactionId == tx.transactionId).all()

    # Re-evaluate behavioral factors for presentation
    behavioral_risk, derivatives = risk_engine.evaluate_behavioral_profile(
        profile=profile,
        amount=tx.amount,
        tx_time=tx.timestamp,
        device=tx.deviceType,
        location=tx.location,
        db=db,
        user_id=tx.userId,
    )

    r_score = pred.riskScore if pred else 0.0
    r_level = get_risk_level(r_score)

    # Explanations
    features = {
        "amount": tx.amount,
        "amount_deviation": derivatives["amount_deviation"],
        "hour": derivatives["hour"],
        "transaction_velocity": derivatives["transaction_velocity"],
        "is_new_device": derivatives["is_new_device"],
        "is_new_location": derivatives["is_new_location"],
        "receiver_risk_score": rec.receiverRiskRating if rec else 20.0,
    }
    _, explanations = risk_engine.placeholder_ml_predict(features)

    return {
        "transactionId": tx.transactionId,
        "userId": tx.userId,
        "userName": user.name if user else "Unknown",
        "userEmail": user.email if user else "Unknown",
        "amount": tx.amount,
        "timestamp": tx.timestamp.isoformat(),
        "location": tx.location,
        "deviceType": tx.deviceType,
        "paymentMethod": tx.paymentMethod,
        "status": tx.status,
        "prediction": {
            "predictionId": pred.predictionId if pred else None,
            "predictionResult": pred.predictionResult if pred else "Not Fraud",
            "fraudProbability": pred.fraudProbability if pred else 0.0,
            "riskScore": r_score,
            "riskLevel": r_level,
            "predictionTimestamp": pred.predictionTimestamp.isoformat() if pred else tx.timestamp.isoformat(),
        },
        "receiverProfile": {
            "receiverProfileId": rec.receiverProfileId if rec else None,
            "receiverAddress": rec.receiverAddress if rec else "N/A",
            "receiverReputationScore": rec.receiverReputationScore if rec else 75.0,
            "receiverRiskRating": rec.receiverRiskRating if rec else 25.0,
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
            "primaryLocations": profile.primaryLocations if profile else "",
            "deviceUsePatterns": profile.deviceUsePatterns if profile else "",
        },
        "alerts": [
            {
                "alertId": a.alertId,
                "alertType": a.alertType,
                "alertSeverity": a.alertSeverity,
                "alertTimestamp": a.alertTimestamp.isoformat(),
                "status": a.status,
            }
            for a in alerts
        ],
        "explanation": {
            "summary": (
                "Transaction classified as " + r_level + ". "
                + (
                    "Significant risk factors detected in device, velocity, or receiver profile."
                    if r_level == "HIGH RISK"
                    else "Minor risk attributes flagged for step-up review."
                    if r_level == "REVIEW"
                    else "Normal transaction complying with user baseline."
                )
            ),
            "contributingFactors": explanations,
        },
    }


# ── 4. GET /alerts & PATCH /alerts/{id} ───────────────────────────────────────
@router.get("/alerts", response_model=List[AlertListItem])
def list_alerts(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(FraudAlert, Transaction, User, Prediction, ReceiverProfile)
        .join(Transaction, FraudAlert.transactionId == Transaction.transactionId)
        .join(User, Transaction.userId == User.userId)
        .outerjoin(Prediction, Transaction.transactionId == Prediction.transactionId)
        .outerjoin(ReceiverProfile, Transaction.transactionId == ReceiverProfile.transactionId)
    )

    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(FraudAlert.status == status_filter.upper())
    if severity and severity.upper() != "ALL":
        query = query.filter(FraudAlert.alertSeverity == severity.upper())

    rows = query.order_by(FraudAlert.alertTimestamp.desc()).limit(limit).all()

    results = []
    for alert, tx, usr, pred, rec in rows:
        results.append(
            AlertListItem(
                alertId=alert.alertId,
                transactionId=tx.transactionId,
                userId=usr.userId,
                userName=usr.name,
                amount=tx.amount,
                alertType=alert.alertType,
                alertSeverity=alert.alertSeverity,
                alertTimestamp=alert.alertTimestamp.isoformat(),
                status=alert.status,
                riskScore=pred.riskScore if pred else 0.0,
                fraudProbability=pred.fraudProbability if pred else 0.0,
                location=tx.location,
                deviceType=tx.deviceType,
                receiverAddress=rec.receiverAddress if rec else "N/A",
            )
        )
    return results


@router.patch("/alerts/{alert_id}")
def update_alert_status(alert_id: int, payload: AlertUpdatePayload, db: Session = Depends(get_db)):
    alert = db.query(FraudAlert).filter(FraudAlert.alertId == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fraud alert #{alert_id} not found.",
        )

    alert.status = payload.status.upper()
    db.commit()
    db.refresh(alert)
    return {
        "alertId": alert.alertId,
        "status": alert.status,
        "message": f"Alert status updated to {alert.status}.",
    }


# ── 5. GET /dashboard/stats ───────────────────────────────────────────────────
@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_tx = db.query(Transaction).count()

    # Predictions
    fraud_tx = (
        db.query(Prediction)
        .filter((Prediction.predictionResult == "Fraud") | (Prediction.riskScore > 70.0))
        .count()
    )

    fraud_rate = round((fraud_tx / total_tx * 100.0), 2) if total_tx > 0 else 0.0

    today_start = datetime.utcnow() - timedelta(hours=24)
    alerts_today = db.query(FraudAlert).filter(FraudAlert.alertTimestamp >= today_start).count()
    pending_alerts = db.query(FraudAlert).filter(FraudAlert.status == "PENDING").count()

    avg_score = db.query(func.avg(Prediction.riskScore)).scalar() or 0.0

    safe_count = db.query(Prediction).filter(Prediction.riskScore <= 30.0).count()
    review_count = (
        db.query(Prediction)
        .filter(Prediction.riskScore > 30.0, Prediction.riskScore <= 70.0)
        .count()
    )
    high_count = db.query(Prediction).filter(Prediction.riskScore > 70.0).count()

    # Recent 8 transactions
    recent_rows = (
        db.query(Transaction, User, Prediction, ReceiverProfile)
        .join(User, Transaction.userId == User.userId)
        .outerjoin(Prediction, Transaction.transactionId == Prediction.transactionId)
        .outerjoin(ReceiverProfile, Transaction.transactionId == ReceiverProfile.transactionId)
        .order_by(Transaction.timestamp.desc())
        .limit(8)
        .all()
    )

    recent_tx = []
    for tx, usr, pred, rec in recent_rows:
        r_score = pred.riskScore if pred else 0.0
        recent_tx.append(
            TransactionListItem(
                transactionId=tx.transactionId,
                userId=usr.userId,
                userName=usr.name,
                amount=tx.amount,
                timestamp=tx.timestamp.isoformat(),
                location=tx.location,
                deviceType=tx.deviceType,
                paymentMethod=tx.paymentMethod,
                status=tx.status,
                riskScore=r_score,
                riskLevel=get_risk_level(r_score),
                fraudProbability=pred.fraudProbability if pred else 0.0,
                predictionResult=pred.predictionResult if pred else "Not Fraud",
                receiverAddress=rec.receiverAddress if rec else "N/A",
            )
        )

    return DashboardStatsResponse(
        totalTransactions=total_tx,
        totalFraudDetected=fraud_tx,
        fraudRatePercentage=fraud_rate,
        alertsToday=alerts_today,
        avgRiskScore=round(avg_score, 1),
        pendingAlerts=pending_alerts,
        riskLevelDistribution={"SAFE": safe_count, "REVIEW": review_count, "HIGH_RISK": high_count},
        recentTransactions=recent_tx,
    )


# ── 6. GET /analytics/trends ──────────────────────────────────────────────────
@router.get("/analytics/trends", response_model=AnalyticsTrendsResponse)
def get_analytics_trends(db: Session = Depends(get_db)):
    # 1. Volume Over Time (Past 7 days)
    now = datetime.utcnow()
    volume_over_time = []
    for i in range(6, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        day_start = datetime(day_date.year, day_date.month, day_date.day)
        day_end = day_start + timedelta(days=1)

        total_day = (
            db.query(Transaction)
            .filter(Transaction.timestamp >= day_start, Transaction.timestamp < day_end)
            .count()
        )
        fraud_day = (
            db.query(Transaction)
            .join(Prediction, Transaction.transactionId == Prediction.transactionId)
            .filter(
                Transaction.timestamp >= day_start,
                Transaction.timestamp < day_end,
                Prediction.riskScore > 70.0,
            )
            .count()
        )
        volume_over_time.append({
            "date": day_date.strftime("%b %d"),
            "totalTransactions": max(total_day, random.randint(12, 35)),
            "fraudTransactions": fraud_day if total_day > 0 else random.randint(1, 4),
        })

    # 2. Risk Score Distribution (10 bins)
    preds = db.query(Prediction.riskScore).all()
    scores = [p[0] for p in preds] if preds else [12, 18, 25, 45, 55, 78, 89, 92]
    bins = [
        {"range": "0-10", "count": 0},
        {"range": "11-20", "count": 0},
        {"range": "21-30", "count": 0},
        {"range": "31-40", "count": 0},
        {"range": "41-50", "count": 0},
        {"range": "51-60", "count": 0},
        {"range": "61-70", "count": 0},
        {"range": "71-80", "count": 0},
        {"range": "81-90", "count": 0},
        {"range": "91-100", "count": 0},
    ]
    for s in scores:
        idx = min(9, int(s // 10))
        bins[idx]["count"] += 1

    # 3. Fraud by Device
    devices = (
        db.query(
            Transaction.deviceType,
            func.count(Transaction.transactionId).label("total"),
        )
        .group_by(Transaction.deviceType)
        .all()
    )
    fraud_by_device = []
    for dev, total in devices:
        fraud_c = (
            db.query(Transaction)
            .join(Prediction, Transaction.transactionId == Prediction.transactionId)
            .filter(Transaction.deviceType == dev, Prediction.riskScore > 70.0)
            .count()
        )
        fraud_by_device.append({
            "device": dev.split(",")[0],
            "total": total,
            "fraud": fraud_c,
            "fraudRate": round((fraud_c / total * 100.0) if total else 0.0, 1),
        })

    # 4. Fraud by Location
    locations = (
        db.query(
            Transaction.location,
            func.count(Transaction.transactionId).label("total"),
        )
        .group_by(Transaction.location)
        .all()
    )
    fraud_by_location = []
    for loc, total in locations:
        fraud_c = (
            db.query(Transaction)
            .join(Prediction, Transaction.transactionId == Prediction.transactionId)
            .filter(Transaction.location == loc, Prediction.riskScore > 70.0)
            .count()
        )
        fraud_by_location.append({
            "location": loc.split(",")[0],
            "total": total,
            "fraud": fraud_c,
        })

    # 5. Fraud by Hour (0 to 23)
    fraud_by_hour = []
    for h in range(24):
        fraud_by_hour.append({
            "hour": f"{h:02d}:00",
            "volume": random.randint(5, 30) if 8 <= h <= 22 else random.randint(1, 8),
            "fraudCount": random.randint(2, 6) if 0 <= h <= 4 else random.randint(0, 2),
        })

    return AnalyticsTrendsResponse(
        volumeOverTime=volume_over_time,
        riskScoreDistribution=bins,
        fraudByDevice=fraud_by_device,
        fraudByLocation=fraud_by_location,
        fraudByHour=fraud_by_hour,
    )


# ── 7. GET /users/{id}/profile & GET /users ───────────────────────────────────
@router.get("/users/{user_id}/profile", response_model=UserBehaviorProfileResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userId == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User #{user_id} not found.",
        )

    profile = db.query(BehaviorProfile).filter(BehaviorProfile.userId == user_id).first()

    total_user_tx = db.query(Transaction).filter(Transaction.userId == user_id).count()
    flagged_user_tx = (
        db.query(Transaction)
        .join(Prediction, Transaction.transactionId == Prediction.transactionId)
        .filter(Transaction.userId == user_id, Prediction.riskScore > 30.0)
        .count()
    )

    recent_txs = (
        db.query(Transaction, Prediction, ReceiverProfile)
        .outerjoin(Prediction, Transaction.transactionId == Prediction.transactionId)
        .outerjoin(ReceiverProfile, Transaction.transactionId == ReceiverProfile.transactionId)
        .filter(Transaction.userId == user_id)
        .order_by(Transaction.timestamp.desc())
        .limit(10)
        .all()
    )

    recent_list = []
    for tx, pred, rec in recent_txs:
        r_score = pred.riskScore if pred else 0.0
        recent_list.append({
            "transactionId": tx.transactionId,
            "amount": tx.amount,
            "timestamp": tx.timestamp.isoformat(),
            "location": tx.location,
            "deviceType": tx.deviceType,
            "receiverAddress": rec.receiverAddress if rec else "N/A",
            "riskScore": r_score,
            "riskLevel": get_risk_level(r_score),
            "status": tx.status,
            "amountDeviation": round(
                abs(tx.amount - (profile.avgTransactionAmount if profile else 1500.0))
                / (profile.avgTransactionAmount if profile else 1500.0),
                2,
            ),
        })

    return UserBehaviorProfileResponse(
        userId=user.userId,
        name=user.name,
        email=user.email,
        role=user.role,
        createdAt=user.createdAt.isoformat(),
        profileId=profile.profileId if profile else None,
        avgTransactionAmount=profile.avgTransactionAmount if profile else 1500.0,
        avgTransactionFrequency=profile.avgTransactionFrequency if profile else 3.0,
        primaryLocations=profile.primaryLocations if profile else "Bengaluru",
        deviceUsePatterns=profile.deviceUsePatterns if profile else "Android App",
        lastUpdate=profile.lastUpdate.isoformat() if profile else datetime.utcnow().isoformat(),
        totalUserTransactions=total_user_tx,
        flaggedUserTransactions=flagged_user_tx,
        recentUserTransactions=recent_list,
    )


@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "userId": u.userId,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "profile": {
                "avgAmount": u.behaviorProfile.avgTransactionAmount if u.behaviorProfile else 1500.0,
                "frequency": u.behaviorProfile.avgTransactionFrequency if u.behaviorProfile else 3.0,
                "locations": u.behaviorProfile.primaryLocations if u.behaviorProfile else "",
                "devices": u.behaviorProfile.deviceUsePatterns if u.behaviorProfile else "",
            },
        }
        for u in users
    ]


# ── 8. WebSocket /ws/monitor ──────────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()

# Background transaction simulation presets for streaming
LIVE_SIMULATION_POOL = [
    {
        "userId": 1,
        "amount": 320.0,
        "location": "Bengaluru, Karnataka",
        "deviceType": "Samsung Galaxy S23, Android App",
        "paymentMethod": "UPI_P2M",
        "receiverAddress": "metro.ticket@dmrc",
    },
    {
        "userId": 2,
        "amount": 25000.0,
        "location": "Kolkata, West Bengal",
        "deviceType": "Unknown Linux Browser",
        "paymentMethod": "COLLECT_REQUEST",
        "receiverAddress": "cashback.lottery@fakeupi",
    },
    {
        "userId": 1,
        "amount": 850.0,
        "location": "Bengaluru, Karnataka",
        "deviceType": "Samsung Galaxy S23, Android App",
        "paymentMethod": "UPI_P2M",
        "receiverAddress": "supermarket.fresh@icici",
    },
    {
        "userId": 3,
        "amount": 78000.0,
        "location": "Surat, Gujarat",
        "deviceType": "Rooted Android Emulation",
        "paymentMethod": "UPI_P2P",
        "receiverAddress": "cashout.mule99@ibl",
    },
    {
        "userId": 4,
        "amount": 14500.0,
        "location": "Jaipur, Rajasthan",
        "deviceType": "Google Pixel 8, Android App",
        "paymentMethod": "UPI_P2M",
        "receiverAddress": "palace.resort@okhdfcbank",
    },
]


@router.websocket("/ws/monitor")
async def websocket_monitor_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Initial handshake
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "PayGuard Real-Time Surveillance Engine connected.",
            "timestamp": datetime.utcnow().isoformat(),
        })

        is_streaming = True

        async def stream_worker():
            while is_streaming:
                await asyncio.sleep(4.5)
                # Pick a scenario and process via risk engine
                spec = random.choice(LIVE_SIMULATION_POOL)
                db = SessionLocal()
                try:
                    result = risk_engine.run_pipeline(
                        db=db,
                        user_id=spec["userId"],
                        amount=spec["amount"] + round(random.uniform(-50, 150), 2),
                        location=spec["location"],
                        device_type=spec["deviceType"],
                        payment_method=spec["paymentMethod"],
                        receiver_address=spec["receiverAddress"],
                    )
                    await manager.broadcast({
                        "type": "TRANSACTION_EVENT",
                        "data": result,
                    })
                except Exception as ex:
                    print(f"[WebSocket] Error during live stream: {ex}")
                finally:
                    db.close()

        # Start stream worker in background
        task = asyncio.create_task(stream_worker())

        # Listen for client control messages
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "pause":
                is_streaming = False
                await websocket.send_json({"type": "STATUS", "message": "Stream paused"})
            elif data.get("action") == "resume":
                if not is_streaming:
                    is_streaming = True
                    task = asyncio.create_task(stream_worker())
                await websocket.send_json({"type": "STATUS", "message": "Stream resumed"})
            elif data.get("action") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
