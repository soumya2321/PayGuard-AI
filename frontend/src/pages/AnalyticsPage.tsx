/**
 * AnalyticsPage.tsx - High-level visualization charts for fraud trends over time,
 * risk score distribution, and multi-vector anomalies by device, location, and time of day.
 * Redesigned with Cyber-Pastel Frosted Glass aesthetic matching the console reference image.
 */

import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  MapPin,
  Smartphone,
  Clock,
  RotateCcw,
  Activity,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { apiService } from '../services/api';
import type { PayGuardAnalyticsTrends } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';

export const AnalyticsPage: React.FC = () => {
  const [trends, setTrends] = useState<PayGuardAnalyticsTrends | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTrends = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getAnalyticsTrends();
      setTrends(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics trends.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, []);

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  const tooltipStyle = {
    backgroundColor: '#ffffff',
    borderColor: '#e2e8f0',
    borderRadius: '0.75rem',
    color: '#0f172a',
    fontSize: '12px',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
  };

  return (
    <div className="space-y-7">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-600 text-xs font-bold uppercase tracking-wider font-mono">
            <BarChart3 className="w-4 h-4" />
            <span>Telemetry & Risk Surveillance</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-1">
            Fraud Analytics & Trends
          </h1>
          <p className="text-slate-500 text-xs sm:text-sm mt-1 max-w-2xl">
            Cross-vector behavioral analysis across historical timelines, risk tiers, devices, locations, and diurnal cycles.
          </p>
        </div>

        <button
          onClick={fetchTrends}
          className="self-start sm:self-auto px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200/80 text-slate-700 font-semibold text-xs transition-colors shadow-sm flex items-center space-x-2"
          title="Refresh Data"
        >
          <RotateCcw className="w-3.5 h-3.5 text-indigo-600" />
          <span>Refresh Data</span>
        </button>
      </div>

      {error && <ErrorAlert message={error} />}

      {/* Grid of Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Fraud Trends Over Time (Area Chart) */}
        <div className="frost-panel rounded-2xl border border-white/80 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-indigo-600" />
              <span>Volume & Fraud Trends Over Time</span>
            </h2>
            <span className="text-[10px] text-slate-500 font-mono font-semibold px-2 py-0.5 rounded bg-slate-100">
              Past 7 Days
            </span>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends?.volumeOverTime || []}>
                <defs>
                  <linearGradient id="totalVolumeColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="fraudVolumeColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ec4899" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#ec4899" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Area
                  type="monotone"
                  dataKey="totalTransactions"
                  name="Total Transactions"
                  stroke="#0ea5e9"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#totalVolumeColor)"
                />
                <Area
                  type="monotone"
                  dataKey="fraudTransactions"
                  name="Flagged Fraud"
                  stroke="#ec4899"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#fraudVolumeColor)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. Risk Score Distribution (Histogram) */}
        <div className="frost-panel rounded-2xl border border-white/80 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Activity className="w-4 h-4 text-emerald-600" />
              <span>Risk Score Distribution (Buckets 0-100)</span>
            </h2>
            <span className="text-[10px] text-slate-600 font-mono font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200/60">
              SAFE / REVIEW / HIGH RISK
            </span>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends?.riskScoreDistribution || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="range" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar
                  dataKey="count"
                  name="Transactions"
                  fill="#6366f1"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. Fraud by Device Type */}
        <div className="frost-panel rounded-2xl border border-white/80 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Smartphone className="w-4 h-4 text-purple-600" />
              <span>Fraud Prevalence by Device Type</span>
            </h2>
            <span className="text-[10px] text-slate-500 font-mono font-semibold px-2 py-0.5 rounded bg-slate-100">
              Hardware Telemetry
            </span>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends?.fraudByDevice || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis dataKey="device" type="category" stroke="#64748b" tick={{ fontSize: 10 }} width={120} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="total" name="Total Volume" fill="#94a3b8" radius={[0, 4, 4, 0]} />
                <Bar dataKey="fraud" name="Fraud Count" fill="#ec4899" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. Fraud by Geographic Location */}
        <div className="frost-panel rounded-2xl border border-white/80 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-amber-500" />
              <span>Fraud Disparity by Location</span>
            </h2>
            <span className="text-[10px] text-slate-500 font-mono font-semibold px-2 py-0.5 rounded bg-slate-100">
              Geographic Telemetry
            </span>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends?.fraudByLocation || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="location" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="total" name="Total Volume" fill="#38bdf8" radius={[5, 5, 0, 0]} />
                <Bar dataKey="fraud" name="Flagged Fraud" fill="#f43f5e" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 5. 24-Hour Diurnal Cycle Spikes (Full width) */}
        <div className="lg:col-span-2 frost-panel rounded-2xl border border-white/80 p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-200/80 pb-3">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Clock className="w-4 h-4 text-sky-600" />
              <span>24-Hour Diurnal Fraud Telemetry (Hour of Day)</span>
            </h2>
            <span className="text-[10px] text-rose-600 font-mono font-semibold px-2 py-0.5 rounded bg-rose-50 border border-rose-200/60">
              Overnight Spikes (00:00 - 05:00 flagged as anomalous)
            </span>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends?.fraudByHour || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="hour" stroke="#64748b" tick={{ fontSize: 9 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="volume" name="Normal Volume" fill="#cbd5e1" radius={[3, 3, 0, 0]} />
                <Bar dataKey="fraudCount" name="Fraud Anomalies" fill="#f59e0b" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
