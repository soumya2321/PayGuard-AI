/**
 * api.ts - Type-safe REST client for the UPI Fraud Detection Backend.
 */

import type {
  DashboardAnalyticsResponse,
  TransactionRecord,
  ModelMetricsResponse,
  SystemHealthResponse,
  PredictionResult,
  TransactionFeatureInput,
  PayGuardDashboardStats,
  PayGuardTransactionHistoryResponse,
  PayGuardTransactionDetail,
  PayGuardAlertItem,
  PayGuardAnalyticsTrends,
  PayGuardUserProfile,
  PayGuardUserItem,
  CreateTransactionPayload,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!response.ok) {
      const errorBody = await response.text();
      let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
      try {
        const parsed = JSON.parse(errorBody);
        if (parsed.detail) errorMsg = parsed.detail;
      } catch {
        // fallback
      }
      throw new Error(errorMsg);
    }

    return (await response.json()) as T;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw err;
    }
    throw new Error('Unknown network error occurred');
  }
}

export const apiService = {
  // System Health
  async getHealth(): Promise<SystemHealthResponse> {
    return request<SystemHealthResponse>('/health');
  },

  // ════════════════════════════════════════════════════════════════════════════
  // PayGuard Core Architecture REST Endpoints
  // ════════════════════════════════════════════════════════════════════════════

  // 1. Dashboard Stats
  async getDashboardStats(): Promise<PayGuardDashboardStats> {
    return request<PayGuardDashboardStats>('/dashboard/stats');
  },

  // 2. Transactions
  async getTransactions(params?: {
    limit?: number;
    offset?: number;
    risk_level?: string;
    search?: string;
  }): Promise<PayGuardTransactionHistoryResponse> {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.offset) query.append('offset', params.offset.toString());
    if (params?.risk_level && params.risk_level !== 'ALL') query.append('risk_level', params.risk_level);
    if (params?.search) query.append('search', params.search);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<PayGuardTransactionHistoryResponse>(`/transactions${qs}`);
  },

  async getTransactionById(id: string | number): Promise<PayGuardTransactionDetail> {
    return request<PayGuardTransactionDetail>(`/transactions/${encodeURIComponent(id)}`);
  },

  async createTransaction(payload: CreateTransactionPayload): Promise<any> {
    return request<any>('/transactions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // 3. Alerts
  async getAlerts(params?: {
    status?: string;
    severity?: string;
    limit?: number;
  }): Promise<PayGuardAlertItem[]> {
    const query = new URLSearchParams();
    if (params?.status && params.status !== 'ALL') query.append('status', params.status);
    if (params?.severity && params.severity !== 'ALL') query.append('severity', params.severity);
    if (params?.limit) query.append('limit', params.limit.toString());
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<PayGuardAlertItem[]>(`/alerts${qs}`);
  },

  async updateAlert(alertId: number | string, status: string, notes?: string): Promise<any> {
    return request<any>(`/alerts/${encodeURIComponent(alertId)}`, {
      method: 'PATCH',
      body: JSON.stringify({ status, analyst_notes: notes }),
    });
  },

  // 4. Analytics
  async getAnalyticsTrends(): Promise<PayGuardAnalyticsTrends> {
    return request<PayGuardAnalyticsTrends>('/analytics/trends');
  },

  // 5. User Profiles
  async getUserProfile(userId: number | string): Promise<PayGuardUserProfile> {
    return request<PayGuardUserProfile>(`/users/${encodeURIComponent(userId)}/profile`);
  },

  async getUsers(): Promise<PayGuardUserItem[]> {
    return request<PayGuardUserItem[]>('/users');
  },

  // WebSocket URL helper
  getMonitorWebSocketUrl(): string {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Backend runs at localhost:8000
    return `${wsProtocol}//127.0.0.1:8000/ws/monitor`;
  },

  // ════════════════════════════════════════════════════════════════════════════
  // Legacy / Simulator compatibility endpoints
  // ════════════════════════════════════════════════════════════════════════════
  async getDashboardAnalytics(): Promise<DashboardAnalyticsResponse> {
    return request<DashboardAnalyticsResponse>('/analytics/dashboard');
  },

  async simulateTransaction(payload: {
    sender_upi_id: string;
    receiver_upi_id: string;
    amount_inr: number;
    location?: string;
    device_type?: string;
    time_of_day?: string;
    features: Partial<TransactionFeatureInput>;
  }): Promise<TransactionRecord> {
    return request<TransactionRecord>('/predict/simulate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async evaluateFeatures(features: Partial<TransactionFeatureInput>): Promise<PredictionResult> {
    return request<PredictionResult>('/predict', {
      method: 'POST',
      body: JSON.stringify(features),
    });
  },

  async getModelMetrics(): Promise<ModelMetricsResponse> {
    return request<ModelMetricsResponse>('/model/metrics');
  },

  async getFeatureDefinitions(): Promise<{
    features: Record<string, { label: string; category: string; description: string; min: number; max: number; default: number }>;
    base_feature_count: number;
    risk_thresholds: { low: number; high: number };
  }> {
    return request('/model/features');
  },
};
