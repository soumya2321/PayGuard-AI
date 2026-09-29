-- =====================================================================
-- UPI FRAUD DETECTION SYSTEM — SUPABASE POSTGRESQL SCHEMA
-- =====================================================================
-- This script configures the schema for transactions, alerts,
-- audit logs, system rules, and model metrics.
-- =====================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── 1. TRANSACTIONS TABLE ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_ref VARCHAR(64) UNIQUE NOT NULL,
    sender_upi_id VARCHAR(128) NOT NULL,
    receiver_upi_id VARCHAR(128) NOT NULL,
    amount_inr NUMERIC(12, 2) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED', -- 'COMPLETED', 'FLAGGED', 'BLOCKED', 'UNDER_REVIEW'
    risk_score FLOAT NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
    risk_tier VARCHAR(16) NOT NULL, -- 'LOW', 'MODERATE', 'HIGH'
    is_fraud_predicted BOOLEAN NOT NULL DEFAULT FALSE,
    actual_fraud_status BOOLEAN NULL, -- Ground truth for analyst review & retraining
    recommendation TEXT NOT NULL,
    action VARCHAR(32) NOT NULL, -- 'APPROVE', 'CHALLENGE_OTP', 'BLOCK_OR_ESCALATE'
    top_risk_factors JSONB NOT NULL DEFAULT '[]'::jsonb,
    feature_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Indices for rapid querying and filtering
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_risk_tier ON transactions(risk_tier);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_sender ON transactions(sender_upi_id);
CREATE INDEX IF NOT EXISTS idx_transactions_receiver ON transactions(receiver_upi_id);
CREATE INDEX IF NOT EXISTS idx_transactions_is_fraud ON transactions(is_fraud_predicted);

-- ── 2. FRAUD ALERTS TABLE ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fraud_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    transaction_ref VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL DEFAULT 'HIGH', -- 'INFO', 'WARNING', 'CRITICAL'
    risk_score FLOAT NOT NULL,
    alert_title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'REVIEWED', 'CONFIRMED_FRAUD', 'FALSE_POSITIVE'
    analyst_notes TEXT NULL,
    reviewed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_alerts_status ON fraud_alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON fraud_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON fraud_alerts(created_at DESC);

-- ── 3. MODEL METRICS AUDIT TABLE ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS model_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version VARCHAR(64) NOT NULL,
    algorithm VARCHAR(128) NOT NULL,
    accuracy FLOAT NOT NULL,
    precision FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    roc_auc FLOAT NOT NULL,
    average_precision FLOAT NOT NULL,
    true_positives INT NOT NULL,
    false_positives INT NOT NULL,
    true_negatives INT NOT NULL,
    false_negatives INT NOT NULL,
    full_metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    trained_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- ── 4. SYSTEM RULES CONFIGURATION ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS system_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_key VARCHAR(64) UNIQUE NOT NULL,
    rule_name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL,
    threshold_value FLOAT NOT NULL,
    comparison_operator VARCHAR(8) NOT NULL, -- '>', '>=', '<', '<=', '=='
    action VARCHAR(32) NOT NULL, -- 'FLAG', 'BLOCK', 'REQUIRE_OTP'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Insert baseline risk rules
INSERT INTO system_rules (rule_key, rule_name, category, threshold_value, comparison_operator, action, description)
VALUES 
    ('HIGH_RISK_THRESHOLD', 'High Risk Model Threshold', 'Model', 0.70, '>=', 'BLOCK', 'Transactions with model fraud probability >= 0.70 require immediate escalation.'),
    ('MODERATE_RISK_THRESHOLD', 'Moderate Risk Review Threshold', 'Model', 0.35, '>=', 'REQUIRE_OTP', 'Transactions with fraud probability between 0.35 and 0.70 trigger 2FA OTP.'),
    ('CLICK_TO_PAY_URGENCY', 'Rapid Link-to-Pay Anomaly', 'Behavioral', 2.0, '<=', 'FLAG', 'Transactions completed under 2 seconds after link click trigger phishing alert.'),
    ('GEO_DISPARITY_LIMIT', 'Severe Geographic Disparity', 'Location', 1.8, '>=', 'FLAG', 'Physical distance mismatch score >= 1.8 flags potential account takeover.')
ON CONFLICT (rule_key) DO NOTHING;

-- ── 5. ROW LEVEL SECURITY (RLS) POLICIES ──────────────────────────────
-- Enable RLS
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE fraud_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_rules ENABLE ROW LEVEL SECURITY;

-- Allow public read/write for demo/educational app (or configure authenticated roles)
CREATE POLICY "Allow anon read transactions" ON transactions FOR SELECT USING (true);
CREATE POLICY "Allow anon insert transactions" ON transactions FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update transactions" ON transactions FOR UPDATE USING (true);

CREATE POLICY "Allow anon read fraud_alerts" ON fraud_alerts FOR SELECT USING (true);
CREATE POLICY "Allow anon insert fraud_alerts" ON fraud_alerts FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update fraud_alerts" ON fraud_alerts FOR UPDATE USING (true);

CREATE POLICY "Allow anon read model_metrics" ON model_metrics FOR SELECT USING (true);
CREATE POLICY "Allow anon insert model_metrics" ON model_metrics FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anon read system_rules" ON system_rules FOR SELECT USING (true);
CREATE POLICY "Allow anon update system_rules" ON system_rules FOR UPDATE USING (true);
