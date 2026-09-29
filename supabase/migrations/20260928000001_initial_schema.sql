-- =====================================================================
-- Migration: 20260928000001_initial_schema.sql
-- Description: Initial schema for UPI Fraud Detection System
-- Tables: users, transactions, fraud_predictions, model_metrics
-- =====================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── 1. USERS TABLE ───────────────────────────────────────────────────
-- Manages customer and merchant profiles.
-- Supports linking with Supabase Auth (auth.users) if enabled.
-- No passwords are stored here.
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(128) NOT NULL,
    phone_number VARCHAR(20),
    primary_upi_id VARCHAR(128) UNIQUE NOT NULL,
    risk_segment VARCHAR(32) NOT NULL DEFAULT 'STANDARD', -- 'LOW_RISK', 'STANDARD', 'WATCHLIST', 'HIGH_RISK'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_users_upi_id ON public.users(primary_upi_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_risk_segment ON public.users(risk_segment);

-- ── 2. TRANSACTIONS TABLE ─────────────────────────────────────────────
-- Captures incoming and historical UPI payment transfers with device telemetry.
CREATE TABLE IF NOT EXISTS public.transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id VARCHAR(64) UNIQUE NOT NULL,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    transaction_amount NUMERIC(12, 2) NOT NULL CHECK (transaction_amount > 0),
    transaction_type VARCHAR(32) NOT NULL DEFAULT 'P2P', -- 'P2P', 'P2M', 'COLLECT_REQUEST', 'QR_SCAN', 'BILL_PAY'
    sender_upi VARCHAR(128) NOT NULL,
    receiver_upi VARCHAR(128) NOT NULL,
    transaction_timestamp TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    device_id VARCHAR(64) NOT NULL,
    location VARCHAR(128) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    merchant_category VARCHAR(64) DEFAULT 'GENERAL', -- 'GROCERY', 'ELECTRONICS', 'GAMING', 'PEER_TRANSFER', 'UTILITY'
    transaction_status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED', -- 'COMPLETED', 'FLAGGED', 'BLOCKED', 'PENDING_VERIFICATION'
    feature_telemetry JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Performance and Query Optimization Indexes
CREATE INDEX IF NOT EXISTS idx_transactions_tx_id ON public.transactions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON public.transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_sender_upi ON public.transactions(sender_upi);
CREATE INDEX IF NOT EXISTS idx_transactions_receiver_upi ON public.transactions(receiver_upi);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON public.transactions(transaction_status);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON public.transactions(transaction_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON public.transactions(created_at DESC);

-- ── 3. FRAUD PREDICTIONS TABLE ─────────────────────────────────────────
-- Stores ML model inference evaluations, probability scores, risk tiers, and factor attributions.
CREATE TABLE IF NOT EXISTS public.fraud_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES public.transactions(id) ON DELETE CASCADE,
    prediction INT NOT NULL CHECK (prediction IN (0, 1)), -- 0: Legitimate, 1: Suspected Fraud
    fraud_probability FLOAT NOT NULL CHECK (fraud_probability >= 0.0 AND fraud_probability <= 1.0),
    model_version VARCHAR(64) NOT NULL,
    risk_tier VARCHAR(16) NOT NULL DEFAULT 'LOW', -- 'LOW', 'MODERATE', 'HIGH'
    recommendation TEXT NOT NULL,
    top_risk_factors JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_fraud_predictions_tx_id ON public.fraud_predictions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_fraud_predictions_prediction ON public.fraud_predictions(prediction);
CREATE INDEX IF NOT EXISTS idx_fraud_predictions_prob ON public.fraud_predictions(fraud_probability);
CREATE INDEX IF NOT EXISTS idx_fraud_predictions_tier ON public.fraud_predictions(risk_tier);
CREATE INDEX IF NOT EXISTS idx_fraud_predictions_created_at ON public.fraud_predictions(created_at DESC);

-- ── 4. MODEL METRICS TABLE ─────────────────────────────────────────────
-- Tracks ML model performance audits, version benchmarks, and classification scores.
CREATE TABLE IF NOT EXISTS public.model_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(128) NOT NULL,
    accuracy FLOAT NOT NULL,
    precision FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    roc_auc FLOAT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_model_metrics_name ON public.model_metrics(model_name);
CREATE INDEX IF NOT EXISTS idx_model_metrics_created_at ON public.model_metrics(created_at DESC);

-- ── 5. ROW LEVEL SECURITY (RLS) POLICIES ──────────────────────────────
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fraud_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_metrics ENABLE ROW LEVEL SECURITY;

-- Allow public / anon read access for the application client
CREATE POLICY "Allow public read users" ON public.users FOR SELECT USING (true);
CREATE POLICY "Allow public insert users" ON public.users FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update users" ON public.users FOR UPDATE USING (true);

CREATE POLICY "Allow public read transactions" ON public.transactions FOR SELECT USING (true);
CREATE POLICY "Allow public insert transactions" ON public.transactions FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update transactions" ON public.transactions FOR UPDATE USING (true);

CREATE POLICY "Allow public read fraud_predictions" ON public.fraud_predictions FOR SELECT USING (true);
CREATE POLICY "Allow public insert fraud_predictions" ON public.fraud_predictions FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read model_metrics" ON public.model_metrics FOR SELECT USING (true);
CREATE POLICY "Allow public insert model_metrics" ON public.model_metrics FOR INSERT WITH CHECK (true);

-- ── 6. SUPABASE AUTH INTEGRATION TRIGGER (OPTIONAL) ───────────────────
-- If Supabase Auth is utilized, this trigger auto-creates a public.users profile
-- upon user confirmation in auth.users without manual password handling.
CREATE OR REPLACE FUNCTION public.handle_new_auth_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name, primary_upi_id, phone_number)
    VALUES (
        new.id,
        new.email,
        COALESCE(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
        COALESCE(new.raw_user_meta_data->>'primary_upi_id', split_part(new.email, '@', 1) || '@upi'),
        new.phone
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Safe trigger creation: only binds if auth schema is present
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth') THEN
        DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
        CREATE TRIGGER on_auth_user_created
            AFTER INSERT ON auth.users
            FOR EACH ROW EXECUTE FUNCTION public.handle_new_auth_user();
    END IF;
END $$;
