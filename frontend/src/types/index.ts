/**
 * types/index.ts - Strict TypeScript interfaces matching PayGuard AI Architecture & ER Schema.
 */

export type RiskTier = 'LOW' | 'MODERATE' | 'HIGH';
export type RiskLevel = 'SAFE' | 'REVIEW' | 'HIGH RISK';
export type RiskAction = 'APPROVE' | 'CHALLENGE_OTP' | 'BLOCK_OR_ESCALATE';
export type TransactionStatus = 'COMPLETED' | 'FLAGGED' | 'BLOCKED' | 'PENDING_VERIFICATION' | 'PROCESSING';
export type TransactionType = 'P2P' | 'P2M' | 'COLLECT_REQUEST' | 'QR_SCAN' | 'BILL_PAY' | 'UPI';
export type UserRiskSegment = 'LOW_RISK' | 'STANDARD' | 'WATCHLIST' | 'HIGH_RISK';
export type AlertStatus = 'PENDING' | 'REVIEWED' | 'CONFIRMED_FRAUD' | 'FALSE_POSITIVE' | 'RESOLVED';
export type AlertSeverity = 'CRITICAL' | 'HIGH' | 'WARNING' | 'MEDIUM' | 'INFO';

/**
 * 1. Legacy User entity
 */
export interface User {
  id: string;
  email?: string | null;
  full_name: string;
  phone_number?: string | null;
  primary_upi_id: string;
  risk_segment: UserRiskSegment;
  is_active: boolean;
  createdAt: string;
  updated_at: string;
}

/**
 * 2. Legacy Transaction entity
 */
export interface Transaction {
  id: string;
  transaction_id: string;
  user_id?: string | null;
  transaction_amount: number;
  transaction_type: TransactionType;
  sender_upi: string;
  receiver_upi: string;
  transaction_timestamp: string;
  device_id: string;
  location: string;
  ip_address: string;
  merchant_category: string;
  transaction_status: TransactionStatus;
  feature_telemetry?: Partial<TransactionFeatureInput>;
  created_at: string;
}

/**
 * 3. Fraud Prediction entity
 */
export interface FraudPrediction {
  id: string;
  transaction_id: string;
  prediction: number;
  fraud_probability: number;
  model_version: string;
  risk_tier: RiskTier;
  recommendation: string;
  top_risk_factors: RiskFactorExplanation[];
  created_at: string;
}

/**
 * 4. Model Metric entity
 */
export interface ModelMetric {
  id: string;
  model_name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  created_at: string;
}

export interface TransactionWithPrediction extends Transaction {
  prediction?: FraudPrediction | null;
}

// ── Behavioral Telemetry & Feature Inputs ────────────────────────────────────
export interface TransactionFeatureInput {
  amount: number;
  session_duration: number;
  receiver_transaction_history: number;
  transaction_amount_vs_sender_history: number;
  geographic_disparity: number;
  transaction_time_of_day: number;
  time_between_link_click_and_transaction: number;
  input_timing_consistency: number;
  keyboard_input_speed: number;
  input_pause_patterns: number;
  screen_active_time: number;
  geographic_location_vs_ip: number;
  background_data_usage: number;
  pin_entry_speed: number;
  request_amount_roundness: number;
  request_acceptance_rate: number;
  time_to_respond_to_request: number;
  user_id_freq: number;
}

export interface RiskFactorExplanation {
  feature: string;
  label: string;
  category: string;
  value: number;
  importance: number;
  impact_score: number;
  is_risk_factor: boolean;
  description: string;
}

export interface PredictionResult {
  prediction: number;
  is_fraud: boolean;
  fraud_probability: number;
  risk_score_percentage: number;
  risk_tier: RiskTier;
  risk_level: string;
  color_code: string;
  recommendation: string;
  action: RiskAction;
  top_risk_factors: RiskFactorExplanation[];
  disclaimer: string;
}

export interface TransactionRecord {
  id: string;
  transaction_ref: string;
  sender_upi_id: string;
  receiver_upi_id: string;
  amount_inr: number;
  location?: string;
  device_type?: string;
  time_of_day?: string;
  status: string;
  risk_score: number;
  risk_tier: RiskTier;
  is_fraud_predicted: boolean;
  actual_fraud_status?: boolean | null;
  recommendation: string;
  action: RiskAction;
  top_risk_factors: RiskFactorExplanation[];
  feature_snapshot: Partial<TransactionFeatureInput>;
  created_at: string;
}

export interface TransactionListResponse {
  items: TransactionRecord[];
  total: number;
  limit: number;
  offset: number;
}

export interface AlertRecord {
  id: string;
  transaction_id: string;
  transaction_ref: string;
  severity: AlertSeverity;
  risk_score: number;
  alert_title: string;
  description: string;
  status: AlertStatus;
  analyst_notes?: string | null;
  reviewed_at?: string | null;
  created_at: string;
}

export interface AnalyticsSummary {
  total_transactions: number;
  fraud_count: number;
  legitimate_count: number;
  fraud_rate_percentage: number;
  average_risk_score: number;
  total_volume_inr: number;
  fraud_volume_inr: number;
  pending_critical_alerts: number;
  database_mode: string;
}

export interface TierDistributionItem {
  name: string;
  value: number;
  color: string;
}

export interface TimeTrendItem {
  date: string;
  total: number;
  flagged: number;
  legitimate: number;
  avg_risk: number;
}

export interface RiskFactorCount {
  factor: string;
  count: number;
}

export interface DashboardAnalyticsResponse {
  summary: AnalyticsSummary;
  tier_distribution: TierDistributionItem[];
  time_trend: TimeTrendItem[];
  top_risk_factors: RiskFactorCount[];
}

export interface ModelMetricsResponse {
  model_name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  average_precision: number;
  cv_roc_auc?: number;
  true_positives: number;
  false_positives: number;
  true_negatives: number;
  false_negatives: number;
  total_samples: number;
  actual_fraud_count: number;
  predicted_fraud_count: number;
  false_positive_rate: number;
  false_negative_rate: number;
  feature_importances: Record<string, number>;
}

export interface SystemHealthResponse {
  status: string;
  service: string;
  version: string;
  model_file: string;
  database_backend: string;
  database_connected: boolean;
  total_records_in_db: number;
  pending_critical_alerts: number;
  disclaimer: string;
}

// ══════════════════════════════════════════════════════════════════════════════
// PayGuard AI Multi-Vector Schema Entities (ER Diagram Specification)
// ══════════════════════════════════════════════════════════════════════════════

export interface PayGuardTransactionItem {
  transactionId: number;
  userId: number;
  userName: string;
  amount: number;
  timestamp: string;
  location: string;
  deviceType: string;
  paymentMethod: string;
  status: string;
  riskScore: number;
  riskLevel: RiskLevel;
  fraudProbability: number;
  predictionResult: string;
  receiverAddress: string;
}

export interface PayGuardTransactionHistoryResponse {
  items: PayGuardTransactionItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface PayGuardTransactionDetail {
  transactionId: number;
  userId: number;
  userName: string;
  userEmail: string;
  amount: number;
  timestamp: string;
  location: string;
  deviceType: string;
  paymentMethod: string;
  status: string;
  prediction: {
    predictionId?: number;
    predictionResult: string;
    fraudProbability: number;
    riskScore: number;
    riskLevel: RiskLevel;
    predictionTimestamp: string;
  };
  receiverProfile: {
    receiverProfileId?: number;
    receiverAddress: string;
    receiverReputationScore: number;
    receiverRiskRating: number;
  };
  behavioralAnalysis: {
    behavioralRiskScore: number;
    amountDeviation: number;
    transactionVelocity: number;
    hour: number;
    isUnusualHour: boolean;
    isNewDevice: boolean;
    isNewLocation: boolean;
    userAvgAmount: number;
    primaryLocations: string;
    deviceUsePatterns: string;
  };
  alerts: Array<{
    alertId: number;
    alertType: string;
    alertSeverity: string;
    alertTimestamp: string;
    status: string;
  }>;
  explanation: {
    summary: string;
    contributingFactors: Array<{
      feature: string;
      label: string;
      importance: number;
      value?: number;
      is_risk_factor?: boolean;
      description: string;
    }>;
  };
}

export interface PayGuardAlertItem {
  alertId: number;
  transactionId: number;
  userId: number;
  userName: string;
  amount: number;
  alertType: string;
  alertSeverity: string;
  alertTimestamp: string;
  status: string;
  riskScore: number;
  fraudProbability: number;
  location: string;
  deviceType: string;
  receiverAddress: string;
}

export interface PayGuardDashboardStats {
  totalTransactions: number;
  totalFraudDetected: number;
  fraudRatePercentage: number;
  alertsToday: number;
  avgRiskScore: number;
  pendingAlerts: number;
  riskLevelDistribution: {
    SAFE: number;
    REVIEW: number;
    HIGH_RISK: number;
  };
  recentTransactions: PayGuardTransactionItem[];
}

export interface PayGuardAnalyticsTrends {
  volumeOverTime: Array<{
    date: string;
    totalTransactions: number;
    fraudTransactions: number;
  }>;
  riskScoreDistribution: Array<{
    range: string;
    count: number;
  }>;
  fraudByDevice: Array<{
    device: string;
    total: number;
    fraud: number;
    fraudRate: number;
  }>;
  fraudByLocation: Array<{
    location: string;
    total: number;
    fraud: number;
  }>;
  fraudByHour: Array<{
    hour: string;
    volume: number;
    fraudCount: number;
  }>;
}

export interface PayGuardUserProfile {
  userId: number;
  name: string;
  email: string;
  role: string;
  createdAt: string;
  profileId?: number;
  avgTransactionAmount: number;
  avgTransactionFrequency: number;
  primaryLocations: string;
  deviceUsePatterns: string;
  lastUpdate: string;
  totalUserTransactions: number;
  flaggedUserTransactions: number;
  recentUserTransactions: Array<{
    transactionId: number;
    amount: number;
    timestamp: string;
    location: string;
    deviceType: string;
    receiverAddress: string;
    riskScore: number;
    riskLevel: RiskLevel;
    status: string;
    amountDeviation: number;
  }>;
}

export interface PayGuardUserItem {
  userId: number;
  name: string;
  email: string;
  role: string;
  profile: {
    avgAmount: number;
    frequency: number;
    locations: string;
    devices: string;
  };
}

export interface CreateTransactionPayload {
  userId: number;
  amount: number;
  location: string;
  deviceType: string;
  paymentMethod?: string;
  receiverAddress?: string;
}
