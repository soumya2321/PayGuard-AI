-- =====================================================================
-- Migration: 20260928000002_seed_data.sql
-- Description: Seed initial demo users, model metrics, and scored transactions
-- =====================================================================

-- ── 1. SEED MODEL METRICS (From verified champion training run) ───────
INSERT INTO public.model_metrics (id, model_name, accuracy, precision, recall, f1_score, roc_auc, created_at)
VALUES 
    ('a0000000-0000-0000-0000-000000000001', 'XGBoost Classifier (Champion)', 0.9729, 0.9083, 0.9373, 0.9226, 0.9965, now() - INTERVAL '1 day'),
    ('a0000000-0000-0000-0000-000000000002', 'Random Forest Classifier (Baseline)', 0.9680, 0.8920, 0.9210, 0.9063, 0.9963, now() - INTERVAL '2 days')
ON CONFLICT (id) DO NOTHING;

-- ── 2. SEED DEMO USERS ────────────────────────────────────────────────
INSERT INTO public.users (id, email, full_name, phone_number, primary_upi_id, risk_segment)
VALUES
    ('b0000000-0000-0000-0000-000000000001', 'rohit.sharma@example.com', 'Rohit Sharma', '+919876543210', 'rohit@okaxis', 'LOW_RISK'),
    ('b0000000-0000-0000-0000-000000000002', 'priya.patel@example.com', 'Priya Patel', '+919876543211', 'priya.p@oksbi', 'STANDARD'),
    ('b0000000-0000-0000-0000-000000000003', 'amit.kumar@example.com', 'Amit Kumar', '+919876543212', 'amit.k@paytm', 'STANDARD'),
    ('b0000000-0000-0000-0000-000000000004', 'sneha.reddy@example.com', 'Sneha Reddy', '+919876543213', 'sneha.r@ybl', 'LOW_RISK'),
    ('b0000000-0000-0000-0000-000000000005', 'vikram.singh@example.com', 'Vikram Singh', '+919876543214', 'vikram.s@ibl', 'WATCHLIST')
ON CONFLICT (id) DO NOTHING;

-- ── 3. SEED TRANSACTIONS & FRAUD PREDICTIONS ──────────────────────────
-- Legitimate Transaction 1
INSERT INTO public.transactions (
    id, transaction_id, user_id, transaction_amount, transaction_type, 
    sender_upi, receiver_upi, transaction_timestamp, device_id, 
    location, ip_address, merchant_category, transaction_status, created_at
) VALUES (
    'c0000000-0000-0000-0000-000000000001', 'UPI-TXN-88492011', 'b0000000-0000-0000-0000-000000000001',
    450.00, 'P2M', 'rohit@okaxis', 'chai.point@paytm', now() - INTERVAL '3 hours',
    'DEV-SM-A52-9981', 'Mumbai, MH, India', '49.36.120.45', 'FOOD_BEVERAGE', 'COMPLETED', now() - INTERVAL '3 hours'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO public.fraud_predictions (
    id, transaction_id, prediction, fraud_probability, model_version, 
    risk_tier, recommendation, top_risk_factors, created_at
) VALUES (
    'd0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001',
    0, 0.0124, 'xgboost-v1.0.0', 'LOW',
    'Transaction matches legitimate customer behavioral profile. Fast-track approval.',
    '[{"feature": "receiver_transaction_history", "label": "Receiver Trust Score", "impact_score": -0.15, "is_risk_factor": false}]'::jsonb,
    now() - INTERVAL '3 hours'
) ON CONFLICT (id) DO NOTHING;

-- High Risk Suspicious Collect Request Scam
INSERT INTO public.transactions (
    id, transaction_id, user_id, transaction_amount, transaction_type, 
    sender_upi, receiver_upi, transaction_timestamp, device_id, 
    location, ip_address, merchant_category, transaction_status, created_at
) VALUES (
    'c0000000-0000-0000-0000-000000000002', 'UPI-TXN-77381920', 'b0000000-0000-0000-0000-000000000002',
    24999.00, 'COLLECT_REQUEST', 'priya.p@oksbi', 'lottery.reward@fakeupi', now() - INTERVAL '2 hours',
    'DEV-IPH-13-8821', 'Bengaluru, KA, India', '103.212.43.12', 'PEER_TRANSFER', 'BLOCKED', now() - INTERVAL '2 hours'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO public.fraud_predictions (
    id, transaction_id, prediction, fraud_probability, model_version, 
    risk_tier, recommendation, top_risk_factors, created_at
) VALUES (
    'd0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000002',
    1, 0.9842, 'xgboost-v1.0.0', 'HIGH',
    'Block transaction immediately or require biometric step-up verification.',
    '[{"feature": "time_between_link_click_and_transaction", "label": "Click-to-Pay Delay", "impact_score": 0.42, "is_risk_factor": true}, {"feature": "receiver_transaction_history", "label": "Receiver Trust Score", "impact_score": 0.38, "is_risk_factor": true}, {"feature": "amount_anomaly", "label": "Amount Anomaly", "impact_score": 0.25, "is_risk_factor": true}]'::jsonb,
    now() - INTERVAL '2 hours'
) ON CONFLICT (id) DO NOTHING;

-- Moderate Risk Transaction (Unusual Location + Round Amount)
INSERT INTO public.transactions (
    id, transaction_id, user_id, transaction_amount, transaction_type, 
    sender_upi, receiver_upi, transaction_timestamp, device_id, 
    location, ip_address, merchant_category, transaction_status, created_at
) VALUES (
    'c0000000-0000-0000-0000-000000000003', 'UPI-TXN-99120483', 'b0000000-0000-0000-0000-000000000003',
    10000.00, 'P2P', 'amit.k@paytm', 'rahul.merchant@barodampay', now() - INTERVAL '1 hour',
    'DEV-ONEPLUS-9901', 'Kolkata, WB, India', '182.74.88.19', 'ELECTRONICS', 'FLAGGED', now() - INTERVAL '1 hour'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO public.fraud_predictions (
    id, transaction_id, prediction, fraud_probability, model_version, 
    risk_tier, recommendation, top_risk_factors, created_at
) VALUES (
    'd0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000003',
    0, 0.5420, 'xgboost-v1.0.0', 'MODERATE',
    'Prompt user with warning banner and require 2-step OTP confirmation.',
    '[{"feature": "geographic_disparity", "label": "Geographic Disparity", "impact_score": 0.22, "is_risk_factor": true}, {"feature": "request_amount_roundness", "label": "Round Amount Indicator", "impact_score": 0.18, "is_risk_factor": true}]'::jsonb,
    now() - INTERVAL '1 hour'
) ON CONFLICT (id) DO NOTHING;
