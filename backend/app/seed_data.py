"""
seed_data.py - Populates the database with initial users, behavioral profiles,
model version metadata, and realistic historical transactions/alerts.
"""

from datetime import datetime, timedelta, date
import json
from app.database import SessionLocal, Base, engine
from app.models.schema_models import (
    User,
    BehaviorProfile,
    Transaction,
    Prediction,
    ReceiverProfile,
    FraudAlert,
    ModelVersion,
)


from app.core.security import hash_password

DEMO_ACCOUNTS_SEED = [
    {
        "name": "Rahul Sharma",
        "email": "rahul.sharma@oksbi",
        "password": "Customer#2026",
        "role": "customer",
        "profile": {
            "avgTransactionAmount": 650.0,
            "avgTransactionFrequency": 4.5,
            "primaryLocations": "Bengaluru, Karnataka; Whitefield, KA",
            "deviceUsePatterns": "Samsung Galaxy S23, Android App",
        },
    },
    {
        "name": "Fresh Mart Merchant",
        "email": "fresh.mart@paytm",
        "password": "Merchant#2026",
        "role": "merchant",
        "profile": {
            "avgTransactionAmount": 450.0,
            "avgTransactionFrequency": 25.0,
            "primaryLocations": "Bengaluru, Karnataka",
            "deviceUsePatterns": "Merchant Terminal, Android POS",
        },
    },
    {
        "name": "Vikram Singh (Security Analyst)",
        "email": "analyst@payguard.ai",
        "password": "Admin@Secure2026",
        "role": "admin",
        "profile": {
            "avgTransactionAmount": 2500.0,
            "avgTransactionFrequency": 2.0,
            "primaryLocations": "Bengaluru, Karnataka",
            "deviceUsePatterns": "MacBook Pro, Web Console",
        },
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@okaxis",
        "password": "Customer#2026",
        "role": "customer",
        "profile": {
            "avgTransactionAmount": 1800.0,
            "avgTransactionFrequency": 2.8,
            "primaryLocations": "Mumbai, Maharashtra; Bandra, MH",
            "deviceUsePatterns": "iPhone 15 Pro, iOS App",
        },
    },
    {
        "name": "Amit Kumar",
        "email": "amit.kumar@ybl",
        "password": "Customer#2026",
        "role": "customer",
        "profile": {
            "avgTransactionAmount": 3200.0,
            "avgTransactionFrequency": 1.5,
            "primaryLocations": "New Delhi, Delhi NCR",
            "deviceUsePatterns": "OnePlus 11, Android App",
        },
    },
    {
        "name": "Sneha Reddy",
        "email": "sneha.reddy@barodampay",
        "password": "Customer#2026",
        "role": "customer",
        "profile": {
            "avgTransactionAmount": 950.0,
            "avgTransactionFrequency": 3.2,
            "primaryLocations": "Hyderabad, Telangana; Gachibowli, TS",
            "deviceUsePatterns": "Google Pixel 8, Android App",
        },
    },
]


def ensure_demo_credentials(db):
    """Ensures all demo users have valid bcrypt password hashes in the database."""
    for account in DEMO_ACCOUNTS_SEED:
        user = db.query(User).filter(User.email.ilike(account["email"])).first()
        valid_bcrypt_hash = hash_password(account["password"])

        if user:
            # Upgrade password hash to bcrypt
            user.passwordHash = valid_bcrypt_hash
            user.role = account["role"]
        else:
            user = User(
                name=account["name"],
                email=account["email"],
                passwordHash=valid_bcrypt_hash,
                role=account["role"],
                createdAt=datetime.utcnow() - timedelta(days=90),
            )
            db.add(user)
            db.flush()

            profile = BehaviorProfile(
                userId=user.userId,
                lastUpdate=datetime.utcnow() - timedelta(days=2),
                avgTransactionAmount=account["profile"]["avgTransactionAmount"],
                avgTransactionFrequency=account["profile"]["avgTransactionFrequency"],
                primaryLocations=account["profile"]["primaryLocations"],
                deviceUsePatterns=account["profile"]["deviceUsePatterns"],
            )
            db.add(profile)

    db.commit()


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        ensure_demo_credentials(db)

        # Check if historical transactions already seeded
        if db.query(Transaction).count() > 0:
            print("[Seed] Database already initialized and demo passwords updated.")
            return

        print("[Seed] Seeding initial users and profiles...")

        # 1. Model Version
        metrics = {
            "accuracy": 0.9842,
            "precision": 0.9083,
            "recall": 0.9373,
            "f1_score": 0.9226,
            "roc_auc": 0.9965,
            "pr_auc": 0.9862,
            "false_positive_rate": 0.0197,
        }
        model_v1 = ModelVersion(
            modelName="XGBoost UPI Fraud Classifier v1.0",
            deploymentDate=date.today() - timedelta(days=30),
            description="Production-grade gradient boosted decision trees trained on multi-vector behavioral telemetry and network features with SMOTE imbalance mitigation.",
            performanceMetrics=json.dumps(metrics),
        )
        db.add(model_v1)
        db.flush()

        # 2. Users and Behavior Profiles
        users_data = [
            {
                "name": "Rahul Sharma",
                "email": "rahul.sharma@oksbi",
                "passwordHash": "$2b$12$e8Yp0r9sW2Q4B9dK7U4/6OG4t6o2H7fD5N9b2.example_hash",
                "role": "USER",
                "profile": {
                    "avgTransactionAmount": 650.0,
                    "avgTransactionFrequency": 4.5,
                    "primaryLocations": "Bengaluru, Karnataka; Whitefield, KA",
                    "deviceUsePatterns": "Samsung Galaxy S23, Android App",
                },
            },
            {
                "name": "Priya Patel",
                "email": "priya.patel@okaxis",
                "passwordHash": "$2b$12$e8Yp0r9sW2Q4B9dK7U4/6OG4t6o2H7fD5N9b2.example_hash",
                "role": "USER",
                "profile": {
                    "avgTransactionAmount": 1800.0,
                    "avgTransactionFrequency": 2.8,
                    "primaryLocations": "Mumbai, Maharashtra; Bandra, MH",
                    "deviceUsePatterns": "iPhone 15 Pro, iOS App",
                },
            },
            {
                "name": "Amit Kumar",
                "email": "amit.kumar@ybl",
                "passwordHash": "$2b$12$e8Yp0r9sW2Q4B9dK7U4/6OG4t6o2H7fD5N9b2.example_hash",
                "role": "USER",
                "profile": {
                    "avgTransactionAmount": 3200.0,
                    "avgTransactionFrequency": 1.5,
                    "primaryLocations": "New Delhi, Delhi NCR",
                    "deviceUsePatterns": "OnePlus 11, Android App",
                },
            },
            {
                "name": "Sneha Reddy",
                "email": "sneha.reddy@barodampay",
                "passwordHash": "$2b$12$e8Yp0r9sW2Q4B9dK7U4/6OG4t6o2H7fD5N9b2.example_hash",
                "role": "USER",
                "profile": {
                    "avgTransactionAmount": 950.0,
                    "avgTransactionFrequency": 3.2,
                    "primaryLocations": "Hyderabad, Telangana; Gachibowli, TS",
                    "deviceUsePatterns": "Google Pixel 8, Android App",
                },
            },
            {
                "name": "Vikram Singh (Analyst)",
                "email": "vikram.singh@payguard.ai",
                "passwordHash": "$2b$12$e8Yp0r9sW2Q4B9dK7U4/6OG4t6o2H7fD5N9b2.example_hash",
                "role": "ADMIN",
                "profile": {
                    "avgTransactionAmount": 2500.0,
                    "avgTransactionFrequency": 2.0,
                    "primaryLocations": "Bengaluru, Karnataka",
                    "deviceUsePatterns": "MacBook Pro, Web Console",
                },
            },
        ]

        seeded_users = []
        for u in users_data:
            user = User(
                name=u["name"],
                email=u["email"],
                passwordHash=u["passwordHash"],
                role=u["role"],
                createdAt=datetime.utcnow() - timedelta(days=90),
            )
            db.add(user)
            db.flush()

            prof = BehaviorProfile(
                userId=user.userId,
                lastUpdate=datetime.utcnow() - timedelta(days=2),
                avgTransactionAmount=u["profile"]["avgTransactionAmount"],
                avgTransactionFrequency=u["profile"]["avgTransactionFrequency"],
                primaryLocations=u["profile"]["primaryLocations"],
                deviceUsePatterns=u["profile"]["deviceUsePatterns"],
            )
            db.add(prof)
            seeded_users.append(user)

        db.flush()

        # 3. Seed some realistic historical transactions with predictions and alerts
        now = datetime.utcnow()
        historical_txns = [
            # Legitimate routine payments
            {
                "user": seeded_users[0],
                "amount": 420.0,
                "offset_hours": 72,
                "location": "Bengaluru, Karnataka",
                "device": "Samsung Galaxy S23, Android App",
                "paymentMethod": "UPI_P2M",
                "status": "COMPLETED",
                "receiver": "fresh.mart@paytm",
                "reputation": 92.0,
                "receiverRisk": 8.0,
                "fraudProb": 0.04,
                "riskScore": 12.5,
                "prediction": "Not Fraud",
                "alert": None,
            },
            {
                "user": seeded_users[0],
                "amount": 750.0,
                "offset_hours": 48,
                "location": "Bengaluru, Karnataka",
                "device": "Samsung Galaxy S23, Android App",
                "paymentMethod": "UPI_P2P",
                "status": "COMPLETED",
                "receiver": "anita.sharma@oksbi",
                "reputation": 88.0,
                "receiverRisk": 12.0,
                "fraudProb": 0.08,
                "riskScore": 18.0,
                "prediction": "Not Fraud",
                "alert": None,
            },
            {
                "user": seeded_users[1],
                "amount": 1650.0,
                "offset_hours": 36,
                "location": "Mumbai, Maharashtra",
                "device": "iPhone 15 Pro, iOS App",
                "paymentMethod": "UPI_P2M",
                "status": "COMPLETED",
                "receiver": "starbucks.india@icici",
                "reputation": 96.0,
                "receiverRisk": 4.0,
                "fraudProb": 0.05,
                "riskScore": 15.2,
                "prediction": "Not Fraud",
                "alert": None,
            },
            # Review transactions
            {
                "user": seeded_users[3],
                "amount": 12500.0,
                "offset_hours": 24,
                "location": "Jaipur, Rajasthan",
                "device": "Google Pixel 8, Android App",
                "paymentMethod": "UPI_P2M",
                "status": "FLAGGED",
                "receiver": "royal.palace.hotel@okhdfcbank",
                "reputation": 70.0,
                "receiverRisk": 30.0,
                "fraudProb": 0.42,
                "riskScore": 54.0,
                "prediction": "Not Fraud",
                "alert": None,
            },
            # Fraudulent transactions with alerts
            {
                "user": seeded_users[1],
                "amount": 25000.0,
                "offset_hours": 12,
                "location": "Kolkata, West Bengal",
                "device": "Unknown Device, Linux Web",
                "paymentMethod": "COLLECT_REQUEST",
                "status": "BLOCKED",
                "receiver": "lottery.reward99@fakeupi",
                "reputation": 15.0,
                "receiverRisk": 85.0,
                "fraudProb": 0.89,
                "riskScore": 88.4,
                "prediction": "Fraud",
                "alert": {
                    "alertType": "SUSPICIOUS_COLLECT_REQUEST",
                    "severity": "CRITICAL",
                    "status": "PENDING",
                },
            },
            {
                "user": seeded_users[2],
                "amount": 88000.0,
                "offset_hours": 4,
                "location": "Surat, Gujarat",
                "device": "Emulated Android x86",
                "paymentMethod": "UPI_P2P",
                "status": "BLOCKED",
                "receiver": "cashout.mule@ibl",
                "reputation": 10.0,
                "receiverRisk": 90.0,
                "fraudProb": 0.94,
                "riskScore": 92.1,
                "prediction": "Fraud",
                "alert": {
                    "alertType": "ACCOUNT_TAKEOVER_ANOMALY",
                    "severity": "CRITICAL",
                    "status": "PENDING",
                },
            },
            {
                "user": seeded_users[0],
                "amount": 18500.0,
                "offset_hours": 1,
                "location": "Noida, Uttar Pradesh",
                "device": "Windows Chrome Web",
                "paymentMethod": "COLLECT_REQUEST",
                "status": "FLAGGED",
                "receiver": "crypto.exchange.p2p@okaxis",
                "reputation": 35.0,
                "receiverRisk": 65.0,
                "fraudProb": 0.74,
                "riskScore": 76.5,
                "prediction": "Fraud",
                "alert": {
                    "alertType": "UNUSUAL_LOCATION_AND_AMOUNT",
                    "severity": "HIGH",
                    "status": "REVIEWED",
                },
            },
        ]

        for item in historical_txns:
            tx_time = now - timedelta(hours=item["offset_hours"])
            tx = Transaction(
                userId=item["user"].userId,
                amount=item["amount"],
                timestamp=tx_time,
                location=item["location"],
                deviceType=item["device"],
                paymentMethod=item["paymentMethod"],
                status=item["status"],
            )
            db.add(tx)
            db.flush()

            # Prediction
            pred = Prediction(
                transactionId=tx.transactionId,
                modelVersionId=model_v1.modelVersionId,
                predictionResult=item["prediction"],
                fraudProbability=item["fraudProb"],
                riskScore=item["riskScore"],
                predictionTimestamp=tx_time,
            )
            db.add(pred)

            # Receiver profile
            rec = ReceiverProfile(
                transactionId=tx.transactionId,
                receiverReputationScore=item["reputation"],
                receiverRiskRating=item["receiverRisk"],
                calculatedAt=tx_time,
                receiverAddress=item["receiver"],
            )
            db.add(rec)

            # Fraud alert
            if item["alert"]:
                alert = FraudAlert(
                    transactionId=tx.transactionId,
                    alertType=item["alert"]["alertType"],
                    alertSeverity=item["alert"]["severity"],
                    alertTimestamp=tx_time,
                    status=item["alert"]["status"],
                )
                db.add(alert)

        db.commit()
        print("[Seed] Database successfully seeded with baseline records!")

    except Exception as e:
        db.rollback()
        print(f"[Seed] Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
