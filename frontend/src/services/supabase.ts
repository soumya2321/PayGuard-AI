/**
 * supabase.ts - Direct Supabase PostgreSQL client for Frontend.
 * Reads environment variables VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.
 * Never hardcodes credentials.
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import type { 
  User, 
  Transaction, 
  FraudPrediction, 
  ModelMetric, 
  TransactionWithPrediction 
} from '../types';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const isSupabaseConfigured = (): boolean => {
  return Boolean(
    supabaseUrl &&
    supabaseAnonKey &&
    supabaseUrl.startsWith('http') &&
    supabaseAnonKey.length > 20
  );
};

export const supabase: SupabaseClient | null = isSupabaseConfigured()
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

/**
 * Direct Supabase database query helpers
 */
export const supabaseDb = {
  // 1. Fetch Users
  async getUsers(limit = 50): Promise<User[]> {
    if (!supabase) return [];
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) throw error;
    return (data || []) as User[];
  },

  // 2. Fetch Transactions with joined Predictions
  async getTransactions(limit = 50, offset = 0): Promise<{ items: TransactionWithPrediction[]; total: number }> {
    if (!supabase) return { items: [], total: 0 };
    const { data, count, error } = await supabase
      .from('transactions')
      .select('*, prediction:fraud_predictions(*)', { count: 'exact' })
      .order('transaction_timestamp', { ascending: false })
      .range(offset, offset + limit - 1);

    if (error) throw error;

    const items = (data || []).map((row) => ({
      ...row,
      prediction: Array.isArray(row.prediction) ? row.prediction[0] || null : row.prediction || null,
    })) as TransactionWithPrediction[];

    return { items, total: count || 0 };
  },

  // 3. Fetch Single Transaction by transaction_id
  async getTransactionById(transactionId: string): Promise<TransactionWithPrediction | null> {
    if (!supabase) return null;
    const { data, error } = await supabase
      .from('transactions')
      .select('*, prediction:fraud_predictions(*)')
      .eq('transaction_id', transactionId)
      .maybeSingle();

    if (error) throw error;
    if (!data) return null;

    return {
      ...data,
      prediction: Array.isArray(data.prediction) ? data.prediction[0] || null : data.prediction || null,
    } as TransactionWithPrediction;
  },

  // 4. Fetch Model Metrics
  async getModelMetrics(): Promise<ModelMetric[]> {
    if (!supabase) return [];
    const { data, error } = await supabase
      .from('model_metrics')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;
    return (data || []) as ModelMetric[];
  },

  // 5. Insert new Transaction
  async insertTransaction(tx: Omit<Transaction, 'id' | 'created_at'>): Promise<Transaction> {
    if (!supabase) throw new Error('Supabase client is not configured.');
    const { data, error } = await supabase
      .from('transactions')
      .insert(tx)
      .select()
      .single();

    if (error) throw error;
    return data as Transaction;
  },

  // 6. Insert new Fraud Prediction
  async insertFraudPrediction(prediction: Omit<FraudPrediction, 'id' | 'created_at'>): Promise<FraudPrediction> {
    if (!supabase) throw new Error('Supabase client is not configured.');
    const { data, error } = await supabase
      .from('fraud_predictions')
      .insert(prediction)
      .select()
      .single();

    if (error) throw error;
    return data as FraudPrediction;
  },
};
