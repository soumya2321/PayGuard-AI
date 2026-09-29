"""
db_service.py - Unified Database Adapter supporting Supabase PostgreSQL with local SQLite persistence fallback.
Tables: users, transactions, fraud_predictions, model_metrics.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import json
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import config

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class DatabaseService:
    def __init__(self):
        self.supabase_client = None
        self.use_supabase = False
        self._init_connection()
        self._init_sqlite_schema()
        self.seed_if_empty()

    def _init_connection(self) -> None:
        if (
            SUPABASE_AVAILABLE
            and config.SUPABASE_URL
            and config.SUPABASE_KEY
            and config.SUPABASE_URL.startswith("http")
            and len(config.SUPABASE_KEY) > 10
        ):
            try:
                self.supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
                self.use_supabase = True
                print(f"[Database] Connected to Supabase PostgreSQL at {config.SUPABASE_URL[:25]}...")
            except Exception as e:
                print(f"[Database] Supabase connection error: {e}. Falling back to SQLite.")
                self.use_supabase = False
        else:
            self.use_supabase = False

    def _get_sqlite_conn(self) -> sqlite3.Connection:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(config.SQLITE_DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite_schema(self) -> None:
        conn = self._get_sqlite_conn()
        cur = conn.cursor()

        # 1. USERS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            full_name TEXT NOT NULL,
            phone_number TEXT,
            primary_upi_id TEXT UNIQUE NOT NULL,
            risk_segment TEXT NOT NULL DEFAULT 'STANDARD',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        # 2. TRANSACTIONS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            transaction_id TEXT UNIQUE NOT NULL,
            user_id TEXT,
            transaction_amount REAL NOT NULL,
            transaction_type TEXT NOT NULL DEFAULT 'P2P',
            sender_upi TEXT NOT NULL,
            receiver_upi TEXT NOT NULL,
            transaction_timestamp TEXT NOT NULL,
            device_id TEXT NOT NULL,
            location TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            merchant_category TEXT DEFAULT 'GENERAL',
            transaction_status TEXT NOT NULL DEFAULT 'COMPLETED',
            feature_telemetry TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
        """)

        # 3. FRAUD PREDICTIONS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS fraud_predictions (
            id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            prediction INTEGER NOT NULL,
            fraud_probability REAL NOT NULL,
            model_version TEXT NOT NULL,
            risk_tier TEXT NOT NULL DEFAULT 'LOW',
            recommendation TEXT NOT NULL,
            top_risk_factors TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE
        )
        """)

        # 4. MODEL METRICS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS model_metrics (
            id TEXT PRIMARY KEY,
            model_name TEXT NOT NULL,
            accuracy REAL NOT NULL,
            precision REAL NOT NULL,
            recall REAL NOT NULL,
            f1_score REAL NOT NULL,
            roc_auc REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        # Indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions(transaction_timestamp DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tx_status ON transactions(transaction_status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pred_tx_id ON fraud_predictions(transaction_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pred_tier ON fraud_predictions(risk_tier)")

        conn.commit()
        conn.close()

    def save_transaction(self, tx_data: Dict[str, Any], prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert transaction into transactions table and its evaluation into fraud_predictions table."""
        tx_uuid = str(uuid.uuid4())
        pred_uuid = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        tx_id_str = tx_data.get("transaction_id") or f"UPI-TXN-{uuid.uuid4().hex[:8].upper()}"

        tx_record = {
            "id": tx_uuid,
            "transaction_id": tx_id_str,
            "user_id": tx_data.get("user_id"),
            "transaction_amount": float(tx_data.get("transaction_amount", 1000.0)),
            "transaction_type": tx_data.get("transaction_type", "P2P"),
            "sender_upi": tx_data.get("sender_upi", "sender@upi"),
            "receiver_upi": tx_data.get("receiver_upi", "receiver@upi"),
            "transaction_timestamp": tx_data.get("transaction_timestamp") or now_iso,
            "device_id": tx_data.get("device_id", f"DEV-ANDROID-{uuid.uuid4().hex[:6].upper()}"),
            "location": tx_data.get("location", "Mumbai, MH, India"),
            "ip_address": tx_data.get("ip_address", "49.36.120.15"),
            "merchant_category": tx_data.get("merchant_category", "GENERAL"),
            "transaction_status": tx_data.get("transaction_status", "COMPLETED"),
            "feature_telemetry": tx_data.get("feature_telemetry", {}),
            "created_at": tx_data.get("created_at") or now_iso,
        }

        pred_record = {
            "id": pred_uuid,
            "transaction_id": tx_uuid,
            "prediction": int(prediction_data.get("prediction", 0)),
            "fraud_probability": float(prediction_data.get("fraud_probability", 0.0)),
            "model_version": prediction_data.get("model_version", "xgboost-v1.0.0"),
            "risk_tier": prediction_data.get("risk_tier", "LOW"),
            "recommendation": prediction_data.get("recommendation", "Approve"),
            "top_risk_factors": prediction_data.get("top_risk_factors", []),
            "created_at": prediction_data.get("created_at") or now_iso,
        }

        # 1. Supabase insert if connected
        if self.use_supabase and self.supabase_client:
            try:
                self.supabase_client.table("transactions").insert(tx_record).execute()
                self.supabase_client.table("fraud_predictions").insert(pred_record).execute()
            except Exception as e:
                print(f"[Database] Supabase write failed: {e}. Writing to SQLite.")
                self._save_sqlite(tx_record, pred_record)
        else:
            self._save_sqlite(tx_record, pred_record)

        return {**tx_record, "prediction": pred_record}

    def _save_sqlite(self, tx_record: Dict[str, Any], pred_record: Dict[str, Any]) -> None:
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transactions (
                id, transaction_id, user_id, transaction_amount, transaction_type,
                sender_upi, receiver_upi, transaction_timestamp, device_id,
                location, ip_address, merchant_category, transaction_status,
                feature_telemetry, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tx_record["id"], tx_record["transaction_id"], tx_record["user_id"],
            tx_record["transaction_amount"], tx_record["transaction_type"],
            tx_record["sender_upi"], tx_record["receiver_upi"],
            tx_record["transaction_timestamp"], tx_record["device_id"],
            tx_record["location"], tx_record["ip_address"],
            tx_record["merchant_category"], tx_record["transaction_status"],
            json.dumps(tx_record["feature_telemetry"]), tx_record["created_at"],
        ))

        cur.execute("""
            INSERT INTO fraud_predictions (
                id, transaction_id, prediction, fraud_probability,
                model_version, risk_tier, recommendation, top_risk_factors, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pred_record["id"], pred_record["transaction_id"], pred_record["prediction"],
            pred_record["fraud_probability"], pred_record["model_version"],
            pred_record["risk_tier"], pred_record["recommendation"],
            json.dumps(pred_record["top_risk_factors"]), pred_record["created_at"],
        ))

        conn.commit()
        conn.close()

    def get_transactions(
        self,
        limit: int = 50,
        offset: int = 0,
        risk_tier: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch transactions with joined fraud_predictions."""
        if self.use_supabase and self.supabase_client:
            try:
                query = self.supabase_client.table("transactions").select("*, prediction:fraud_predictions(*)", count="exact")
                if search:
                    query = query.or_(f"transaction_id.ilike.%{search}%,sender_upi.ilike.%{search}%,receiver_upi.ilike.%{search}%")
                query = query.order("transaction_timestamp", desc=True).range(offset, offset + limit - 1)
                res = query.execute()
                items = []
                for row in (res.data or []):
                    pred = row.get("prediction")
                    if isinstance(pred, list) and len(pred) > 0:
                        pred = pred[0]
                    row["prediction"] = pred
                    if risk_tier and risk_tier != "ALL":
                        if not pred or pred.get("risk_tier") != risk_tier:
                            continue
                    items.append(row)
                return {"items": items, "total": res.count or len(items)}
            except Exception as e:
                print(f"[Database] Supabase query failed: {e}. Falling back to SQLite.")

        conn = self._get_sqlite_conn()
        cur = conn.cursor()

        base_sql = """
            FROM transactions t
            LEFT JOIN fraud_predictions p ON t.id = p.transaction_id
            WHERE 1=1
        """
        params: List[Any] = []

        if risk_tier and risk_tier.upper() != "ALL":
            base_sql += " AND p.risk_tier = ?"
            params.append(risk_tier.upper())

        if search:
            base_sql += " AND (t.transaction_id LIKE ? OR t.sender_upi LIKE ? OR t.receiver_upi LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        cur.execute(f"SELECT COUNT(*) as cnt {base_sql}", params)
        total = cur.fetchone()["cnt"]

        select_sql = f"""
            SELECT 
                t.*,
                p.id as pred_id,
                p.prediction,
                p.fraud_probability,
                p.model_version,
                p.risk_tier,
                p.recommendation,
                p.top_risk_factors
            {base_sql}
            ORDER BY t.transaction_timestamp DESC
            LIMIT ? OFFSET ?
        """
        cur.execute(select_sql, params + [limit, offset])
        rows = cur.fetchall()

        items = []
        for r in rows:
            d = dict(r)
            top_factors = json.loads(d["top_risk_factors"]) if d.get("top_risk_factors") else []
            telemetry = json.loads(d["feature_telemetry"]) if d.get("feature_telemetry") else {}

            pred_obj = {
                "id": d.get("pred_id"),
                "transaction_id": d["id"],
                "prediction": d.get("prediction", 0),
                "fraud_probability": d.get("fraud_probability", 0.0),
                "model_version": d.get("model_version", "xgboost-v1.0.0"),
                "risk_tier": d.get("risk_tier", "LOW"),
                "recommendation": d.get("recommendation", "Approve"),
                "top_risk_factors": top_factors,
                "created_at": d["created_at"],
            }

            # Combined record representation
            tx_obj = {
                "id": d["id"],
                "transaction_id": d["transaction_id"],
                "user_id": d["user_id"],
                "transaction_amount": d["transaction_amount"],
                "transaction_type": d["transaction_type"],
                "sender_upi": d["sender_upi"],
                "receiver_upi": d["receiver_upi"],
                "transaction_timestamp": d["transaction_timestamp"],
                "device_id": d["device_id"],
                "location": d["location"],
                "ip_address": d["ip_address"],
                "merchant_category": d["merchant_category"],
                "transaction_status": d["transaction_status"],
                "feature_telemetry": telemetry,
                "created_at": d["created_at"],
                "prediction": pred_obj,
                # Compatibility fields for existing UI components
                "transaction_ref": d["transaction_id"],
                "sender_upi_id": d["sender_upi"],
                "receiver_upi_id": d["receiver_upi"],
                "amount_inr": d["transaction_amount"],
                "status": d["transaction_status"],
                "risk_score": d.get("fraud_probability", 0.0),
                "risk_tier": d.get("risk_tier", "LOW"),
                "is_fraud_predicted": bool(d.get("prediction", 0) == 1),
                "top_risk_factors": top_factors,
                "feature_snapshot": telemetry,
            }
            items.append(tx_obj)

        conn.close()
        return {"items": items, "total": total}

    def get_transaction_by_id(self, tx_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                t.*,
                p.id as pred_id,
                p.prediction,
                p.fraud_probability,
                p.model_version,
                p.risk_tier,
                p.recommendation,
                p.top_risk_factors
            FROM transactions t
            LEFT JOIN fraud_predictions p ON t.id = p.transaction_id
            WHERE t.id = ? OR t.transaction_id = ?
        """, (tx_id, tx_id))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None

        d = dict(row)
        top_factors = json.loads(d["top_risk_factors"]) if d.get("top_risk_factors") else []
        telemetry = json.loads(d["feature_telemetry"]) if d.get("feature_telemetry") else {}

        pred_obj = {
            "id": d.get("pred_id"),
            "transaction_id": d["id"],
            "prediction": d.get("prediction", 0),
            "fraud_probability": d.get("fraud_probability", 0.0),
            "model_version": d.get("model_version", "xgboost-v1.0.0"),
            "risk_tier": d.get("risk_tier", "LOW"),
            "recommendation": d.get("recommendation", "Approve"),
            "top_risk_factors": top_factors,
            "created_at": d["created_at"],
        }

        return {
            "id": d["id"],
            "transaction_id": d["transaction_id"],
            "user_id": d["user_id"],
            "transaction_amount": d["transaction_amount"],
            "transaction_type": d["transaction_type"],
            "sender_upi": d["sender_upi"],
            "receiver_upi": d["receiver_upi"],
            "transaction_timestamp": d["transaction_timestamp"],
            "device_id": d["device_id"],
            "location": d["location"],
            "ip_address": d["ip_address"],
            "merchant_category": d["merchant_category"],
            "transaction_status": d["transaction_status"],
            "feature_telemetry": telemetry,
            "created_at": d["created_at"],
            "prediction": pred_obj,
            "transaction_ref": d["transaction_id"],
            "sender_upi_id": d["sender_upi"],
            "receiver_upi_id": d["receiver_upi"],
            "amount_inr": d["transaction_amount"],
            "status": d["transaction_status"],
            "risk_score": d.get("fraud_probability", 0.0),
            "risk_tier": d.get("risk_tier", "LOW"),
            "is_fraud_predicted": bool(d.get("prediction", 0) == 1),
            "top_risk_factors": top_factors,
            "feature_snapshot": telemetry,
        }

    def get_model_metrics(self) -> List[Dict[str, Any]]:
        """Query audited model evaluation metrics."""
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM model_metrics ORDER BY created_at DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_users(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch users."""
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Aggregate authentic database metrics for the analytics dashboard."""
        conn = self._get_sqlite_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN p.prediction = 1 THEN 1 ELSE 0 END) as fraud_count,
                AVG(p.fraud_probability) as avg_risk_score,
                SUM(t.transaction_amount) as total_volume_inr,
                SUM(CASE WHEN p.prediction = 1 THEN t.transaction_amount ELSE 0 END) as fraud_volume_inr
            FROM transactions t
            LEFT JOIN fraud_predictions p ON t.id = p.transaction_id
        """)
        summary_row = cur.fetchone()

        total_tx = summary_row["total_transactions"] or 0
        fraud_tx = summary_row["fraud_count"] or 0
        avg_score = summary_row["avg_risk_score"] or 0.0
        total_vol = summary_row["total_volume_inr"] or 0.0
        fraud_vol = summary_row["fraud_volume_inr"] or 0.0
        fraud_rate = (fraud_tx / total_tx * 100.0) if total_tx > 0 else 0.0

        # Tier counts
        cur.execute("""
            SELECT p.risk_tier, COUNT(*) as cnt
            FROM fraud_predictions p
            GROUP BY p.risk_tier
        """)
        tier_counts = {"LOW": 0, "MODERATE": 0, "HIGH": 0}
        for r in cur.fetchall():
            if r["risk_tier"] in tier_counts:
                tier_counts[r["risk_tier"]] = r["cnt"]

        # Daily Trend
        cur.execute("""
            SELECT 
                substr(t.transaction_timestamp, 1, 10) as tx_date,
                COUNT(*) as total,
                SUM(CASE WHEN p.prediction = 1 THEN 1 ELSE 0 END) as flagged,
                AVG(p.fraud_probability) as daily_avg_risk
            FROM transactions t
            LEFT JOIN fraud_predictions p ON t.id = p.transaction_id
            GROUP BY tx_date
            ORDER BY tx_date ASC
            LIMIT 14
        """)
        trend_rows = [
            {
                "date": r["tx_date"],
                "total": r["total"],
                "flagged": r["flagged"] or 0,
                "legitimate": r["total"] - (r["flagged"] or 0),
                "avg_risk": round(float(r["daily_avg_risk"] or 0.0), 3),
            }
            for r in cur.fetchall()
        ]

        # Top Risk Factors Aggregation
        cur.execute("""
            SELECT top_risk_factors FROM fraud_predictions 
            WHERE prediction = 1 AND top_risk_factors != '[]'
            LIMIT 200
        """)
        factor_counts: Dict[str, int] = {}
        for r in cur.fetchall():
            try:
                factors = json.loads(r["top_risk_factors"]) if isinstance(r["top_risk_factors"], str) else r["top_risk_factors"]
                for f in factors:
                    label = f.get("label", f.get("feature", "Unknown"))
                    factor_counts[label] = factor_counts.get(label, 0) + 1
            except Exception:
                pass

        top_factors = [{"factor": k, "count": v} for k, v in sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:6]]
        conn.close()

        return {
            "summary": {
                "total_transactions": total_tx,
                "fraud_count": fraud_tx,
                "legitimate_count": total_tx - fraud_tx,
                "fraud_rate_percentage": round(fraud_rate, 2),
                "average_risk_score": round(avg_score, 4),
                "total_volume_inr": round(total_vol, 2),
                "fraud_volume_inr": round(fraud_vol, 2),
                "pending_critical_alerts": tier_counts.get("HIGH", 0),
                "database_mode": "Supabase PostgreSQL" if self.use_supabase else "Local SQLite (Ready for Supabase)",
            },
            "tier_distribution": [
                {"name": "Low Risk", "value": tier_counts.get("LOW", 0), "color": "#10b981"},
                {"name": "Moderate Risk", "value": tier_counts.get("MODERATE", 0), "color": "#f59e0b"},
                {"name": "High Risk", "value": tier_counts.get("HIGH", 0), "color": "#ef4444"},
            ],
            "time_trend": trend_rows,
            "top_risk_factors": top_factors,
        }

    def seed_if_empty(self) -> None:
        """Seed demo users, model metrics, and dataset transactions if tables are empty."""
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as count FROM transactions")
        count = cur.fetchone()["count"]

        if count > 0:
            conn.close()
            return

        # 1. Seed Model Metrics
        cur.execute("""
            INSERT OR IGNORE INTO model_metrics (id, model_name, accuracy, precision, recall, f1_score, roc_auc, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "a0000000-0000-0000-0000-000000000001", "XGBoost Classifier (Champion)",
            0.9729, 0.9083, 0.9373, 0.9226, 0.9965, datetime.now(timezone.utc).isoformat()
        ))

        # 2. Seed Users
        demo_users = [
            ("b0000000-0000-0000-0000-000000000001", "rohit.sharma@example.com", "Rohit Sharma", "+919876543210", "rohit@okaxis", "LOW_RISK"),
            ("b0000000-0000-0000-0000-000000000002", "priya.patel@example.com", "Priya Patel", "+919876543211", "priya.p@oksbi", "STANDARD"),
            ("b0000000-0000-0000-0000-000000000003", "amit.kumar@example.com", "Amit Kumar", "+919876543212", "amit.k@paytm", "STANDARD"),
            ("b0000000-0000-0000-0000-000000000004", "sneha.reddy@example.com", "Sneha Reddy", "+919876543213", "sneha.r@ybl", "LOW_RISK"),
            ("b0000000-0000-0000-0000-000000000005", "vikram.singh@example.com", "Vikram Singh", "+919876543214", "vikram.s@ibl", "WATCHLIST")
        ]
        now_str = datetime.now(timezone.utc).isoformat()
        for u in demo_users:
            cur.execute("""
                INSERT OR IGNORE INTO users (id, email, full_name, phone_number, primary_upi_id, risk_segment, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (u[0], u[1], u[2], u[3], u[4], u[5], now_str, now_str))

        conn.commit()
        conn.close()

        # 3. Seed Transactions from dataset
        try:
            import pandas as pd
            from app.services.prediction_service import get_prediction_service

            svc = get_prediction_service()
            x_test_df = pd.read_csv(config.X_TEST_PATH)
            y_test_df = pd.read_csv(config.Y_TEST_PATH)

            fraud_indices = y_test_df[y_test_df.iloc[:, 0] == 1].index.tolist()[:40]
            legit_indices = y_test_df[y_test_df.iloc[:, 0] == 0].index.tolist()[:80]
            sampled_indices = fraud_indices + legit_indices

            base_time = datetime.now(timezone.utc) - timedelta(days=7)
            upi_handles = ["paytm", "okaxis", "okhdfcbank", "ybl", "ibl", "barodampay"]
            names = ["rohit", "priya", "amit", "sneha", "vikram", "ananya", "rahul", "pooja", "karan", "meera"]
            cities = ["Mumbai, MH", "Delhi, DL", "Bengaluru, KA", "Hyderabad, TS", "Chennai, TN", "Pune, MH", "Kolkata, WB"]
            categories = ["FOOD_BEVERAGE", "SHOPPING", "UTILITY", "PEER_TRANSFER", "GROCERY", "ELECTRONICS"]

            for i, idx in enumerate(sampled_indices):
                raw_row = x_test_df.iloc[idx].to_dict()
                pred = svc.predict_single(raw_row)

                s_name = names[i % len(names)]
                r_name = names[(i + 3) % len(names)]
                s_handle = upi_handles[i % len(upi_handles)]
                r_handle = upi_handles[(i + 2) % len(upi_handles)]

                scaled_amt = float(raw_row.get("amount", 0.0))
                amount_inr = round(max(50.0, (scaled_amt + 2.0) * 1200.0 + (i * 37 % 500)), 2)
                tx_timestamp = (base_time + timedelta(hours=i * 1.4)).isoformat()
                assigned_user_id = demo_users[i % len(demo_users)][0]

                tx_data = {
                    "transaction_id": f"UPI-TXN-{uuid.uuid4().hex[:8].upper()}",
                    "user_id": assigned_user_id,
                    "transaction_amount": amount_inr,
                    "transaction_type": "COLLECT_REQUEST" if pred["is_fraud"] else ("P2M" if i % 2 == 0 else "P2P"),
                    "sender_upi": f"{s_name}.{i*7 % 99}@{s_handle}",
                    "receiver_upi": f"{r_name}.merchant@{r_handle}",
                    "transaction_timestamp": tx_timestamp,
                    "device_id": f"DEV-{s_name[:3].upper()}-{1000 + i}",
                    "location": f"{cities[i % len(cities)]}, India",
                    "ip_address": f"49.36.{100 + (i % 150)}.{10 + (i % 200)}",
                    "merchant_category": categories[i % len(categories)],
                    "transaction_status": "FLAGGED" if pred["is_fraud"] else "COMPLETED",
                    "feature_telemetry": raw_row,
                    "created_at": tx_timestamp,
                }

                self.save_transaction(tx_data, pred)
        except Exception as e:
            print(f"[Database] Error seeding data: {e}")


_db_instance = None

def get_db_service() -> DatabaseService:
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseService()
    return _db_instance
