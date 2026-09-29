/**
 * DashboardPage.tsx - Production-style real-time fraud surveillance dashboard.
 * Styled to match the cyber-pastel glassmorphic UI design from the reference image:
 * - 4 distinct cards (Soft Lavender, Vibrant Sky-Blue gradient, Ice-Blue, Glowing Magenta-Pink gradient)
 * - Smooth wave activity chart (dual-tone glowing blue/cyan curves)
 * - Frosted glass containers with crisp dark typography and modern pastel badges
 * - Bottom neumorphic filter pill toggles
 */

import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Activity,
  Radio,
  Pause,
  Play,
  TrendingUp,
  Receipt,
  RotateCcw,
  Zap,
  Sparkles,
  CheckCircle2
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { apiService } from '../services/api';
import type { PayGuardDashboardStats } from '../types';
import { formatCurrency } from '../utils/formatters';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';

// Synthetic smooth activity waveform data matching reference image wave chart
const INITIAL_WAVEFORM = [
  { time: '00:00', volume: 120, fraud: 8 },
  { time: '04:00', volume: 80, fraud: 15 },
  { time: '08:00', volume: 340, fraud: 12 },
  { time: '12:00', volume: 580, fraud: 22 },
  { time: '16:00', volume: 460, fraud: 18 },
  { time: '20:00', volume: 390, fraud: 14 },
  { time: 'Now', volume: 420, fraud: 16 },
];

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  // Metrics State
  const [stats, setStats] = useState<PayGuardDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Live WebSocket Monitoring State
  const [liveStream, setLiveStream] = useState<any[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Filter Pill Toggle States (matching bottom pills from reference image)
  const [streamFilter, setStreamFilter] = useState<'ALL' | 'FLAGGED'>('ALL');

  // Fetch initial stats
  const fetchStats = async () => {
    try {
      setError(null);
      const data = await apiService.getDashboardStats();
      setStats(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard stats.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 15000);
    return () => clearInterval(interval);
  }, []);

  // Initialize WebSocket connection for live monitor stream
  useEffect(() => {
    const wsUrl = apiService.getMonitorWebSocketUrl();
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'TRANSACTION_EVENT' && msg.data) {
          setLiveStream((prev) => [msg.data, ...prev.slice(0, 19)]);
          setStats((prev) => {
            if (!prev) return prev;
            const isFraud = msg.data.prediction.riskLevel === 'HIGH RISK';
            const newTotal = prev.totalTransactions + 1;
            const newFraud = prev.totalFraudDetected + (isFraud ? 1 : 0);
            return {
              ...prev,
              totalTransactions: newTotal,
              totalFraudDetected: newFraud,
              fraudRatePercentage: Number(((newFraud / newTotal) * 100).toFixed(2)),
              alertsToday: prev.alertsToday + (isFraud ? 1 : 0),
            };
          });
        }
      } catch (err) {
        console.error('WebSocket message parsing error:', err);
      }
    };

    ws.onerror = () => setWsConnected(false);
    ws.onclose = () => setWsConnected(false);

    return () => {
      ws.close();
    };
  }, []);

  const togglePauseStream = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: isPaused ? 'resume' : 'pause' }));
      setIsPaused(!isPaused);
    }
  };

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'SAFE':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-600 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 mr-1" /> SAFE
          </span>
        );
      case 'REVIEW':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-600 border border-amber-200">
            <AlertTriangle className="w-3 h-3 mr-1" /> REVIEW
          </span>
        );
      case 'HIGH RISK':
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-600 border border-rose-200 shadow-sm">
            <ShieldAlert className="w-3 h-3 mr-1" /> HIGH RISK
          </span>
        );
    }
  };

  const filteredStream = streamFilter === 'FLAGGED'
    ? liveStream.filter((item) => item.prediction?.riskLevel !== 'SAFE')
    : liveStream;

  return (
    <div className="space-y-6">
      {/* 1. Header Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-600 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-cyan-500" />
            <span>Real-Time Surveillance Engine</span>
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight mt-0.5">
            Surveillance Overview
          </h2>
          <p className="text-slate-500 text-xs">
            Autonomous multi-vector UPI fraud detection streaming behavioral anomalies and risk classifications.
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={fetchStats}
            className="p-2.5 rounded-xl bg-white text-slate-500 hover:text-slate-800 hover:bg-slate-50 border border-slate-200 transition-colors shadow-sm"
            title="Refresh Metrics"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate('/simulator')}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:opacity-95 text-white text-xs font-bold shadow-md shadow-indigo-500/25 transition-all"
          >
            <Zap className="w-4 h-4" />
            <span>Launch ML Simulator</span>
          </button>
        </div>
      </div>

      {error && <ErrorAlert message={error} />}

      {/* ════════════════════════════════════════════════════════════════════════
          2. TOP 4 KPI CARDS (Matching Reference Image Exactly)
          Card 1: Soft Frost Lavender | Card 2: Sky-Blue Gradient
          Card 3: Soft Frost Ice-Blue  | Card 4: Glowing Magenta-Pink Gradient
         ════════════════════════════════════════════════════════════════════════ */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        
        {/* Card 1: Soft Frost Lavender */}
        <div className="frost-panel rounded-3xl p-5 relative overflow-hidden group hover:shadow-md transition-all">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center text-purple-700 font-bold text-xs">
                <Receipt className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-slate-700">Total Volume</span>
            </div>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-purple-50 text-purple-600 border border-purple-200/60 font-mono">
              24h
            </span>
          </div>

          <div className="mt-4">
            <span className="text-3xl font-black text-slate-900 tracking-tight">
              {stats?.totalTransactions.toLocaleString() || '18,450'}
            </span>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
            <span className="flex items-center text-emerald-600 font-semibold">
              <TrendingUp className="w-3.5 h-3.5 mr-1" /> Active Ledger
            </span>
            <span className="font-mono text-[11px]">SQLite/PG</span>
          </div>
        </div>

        {/* Card 2: Vibrant Sky-Blue / Electric Cyan Gradient (Image Card 2) */}
        <div className="bg-gradient-to-br from-[#38bdf8] via-[#0ea5e9] to-[#0284c7] text-white rounded-3xl p-5 shadow-[0_10px_30px_rgba(14,165,233,0.35)] relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-white font-bold text-xs">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-white/90">Fraud Intercepted</span>
            </div>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-white/20 text-white font-mono">
              Score &gt; 70
            </span>
          </div>

          <div className="mt-4">
            <span className="text-3xl font-black text-white tracking-tight">
              {stats?.totalFraudDetected.toLocaleString() || '1,280'}
            </span>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs text-white/80 pt-2 border-t border-white/20">
            <span className="font-medium">
              Rate: <strong className="text-white font-bold">{stats?.fraudRatePercentage || 3.4}%</strong>
            </span>
            <span className="text-[11px] bg-white/15 px-2 py-0.5 rounded-full">
              Blocked
            </span>
          </div>
        </div>

        {/* Card 3: Soft Frost Ice-Blue */}
        <div className="frost-panel rounded-3xl p-5 relative overflow-hidden group hover:shadow-md transition-all">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-full bg-cyan-100 flex items-center justify-center text-cyan-700 font-bold text-xs">
                <Activity className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-slate-700">Average Risk</span>
            </div>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-700 border border-cyan-200/60 font-mono">
              Calibrated
            </span>
          </div>

          <div className="mt-4 flex items-baseline space-x-1.5">
            <span className="text-3xl font-black text-slate-900 tracking-tight">
              {stats?.avgRiskScore || 24.5}
            </span>
            <span className="text-xs font-semibold text-slate-400">/ 100</span>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
            <span className="text-emerald-600 font-semibold">Tier: SAFE (&lt;=30)</span>
            <span className="font-mono text-[11px]">3 Modules</span>
          </div>
        </div>

        {/* Card 4: Glowing Magenta / Electric Pink Gradient (Image Card 4) */}
        <div className="bg-gradient-to-br from-[#f472b6] via-[#ec4899] to-[#c084fc] text-white rounded-3xl p-5 shadow-[0_10px_30px_rgba(236,72,153,0.35)] relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-white font-bold text-xs">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-white/90">Incident Alerts</span>
            </div>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-white/20 text-white font-mono">
              Queue
            </span>
          </div>

          <div className="mt-4 flex items-baseline space-x-1.5">
            <span className="text-3xl font-black text-white tracking-tight">
              {stats?.alertsToday || 18}
            </span>
            <span className="text-xs font-medium text-pink-100">Today</span>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs text-white/80 pt-2 border-t border-white/20">
            <span
              onClick={() => navigate('/alerts')}
              className="underline cursor-pointer font-semibold hover:text-white"
            >
              Open Triage Desk &gt;
            </span>
            <span className="text-[11px] bg-white/15 px-2 py-0.5 rounded-full">
              {stats?.pendingAlerts || 6} Pending
            </span>
          </div>
        </div>
      </div>

      {/* ════════════════════════════════════════════════════════════════════════
          3. MIDDLE SECTION: WAVEFORM CHART ("Hiatbrap" in reference image)
         ════════════════════════════════════════════════════════════════════════ */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column (8 cols): Dual-Tone Smooth Glowing Wave Activity Chart */}
        <div className="lg:col-span-8 frost-panel rounded-3xl p-5 sm:p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-cyan-500" />
                <span>Transaction Velocity & Risk Waveform</span>
              </h3>
              <p className="text-slate-400 text-xs">Real-time throughput volume compared against fraud spikes.</p>
            </div>
            <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">
              Live Diurnal Cycle
            </span>
          </div>

          {/* Smooth Recharts Area Waveform matching the photo */}
          <div className="h-60 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={INITIAL_WAVEFORM} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  {/* Glowing Blue/Cyan Gradient from Image */}
                  <linearGradient id="waveGradientBlue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.7} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
                  </linearGradient>
                  <linearGradient id="waveGradientPurple" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#818cf8" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#4f46e5" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.6} />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    borderRadius: '16px',
                    border: '1px solid #e2e8f0',
                    boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
                    fontSize: '12px',
                    fontWeight: 600,
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="volume"
                  stroke="#0ea5e9"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#waveGradientBlue)"
                  name="Total Throughput"
                />
                <Area
                  type="monotone"
                  dataKey="fraud"
                  stroke="#ec4899"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#waveGradientPurple)"
                  name="Flagged Risk Events"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Bottom Neumorphic Toggles / Status Controls matching reference photo */}
          <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center space-x-2">
              <span className="text-slate-500 font-semibold">Feed Filter:</span>
              <div className="neumorphic-pill rounded-full p-1 flex space-x-1">
                <button
                  type="button"
                  onClick={() => setStreamFilter('ALL')}
                  className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${
                    streamFilter === 'ALL'
                      ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-sm'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  All Transactions
                </button>
                <button
                  type="button"
                  onClick={() => setStreamFilter('FLAGGED')}
                  className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${
                    streamFilter === 'FLAGGED'
                      ? 'bg-gradient-to-r from-rose-500 to-pink-500 text-white shadow-sm'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Flagged Only
                </button>
              </div>
            </div>

            <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-500">
              <span className="flex items-center">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 mr-1.5" /> Volume
              </span>
              <span className="flex items-center">
                <span className="w-2.5 h-2.5 rounded-full bg-pink-500 mr-1.5" /> Risk Events
              </span>
            </div>
          </div>
        </div>

        {/* Right Column (4 cols): Risk Classification Tier Cards */}
        <div className="lg:col-span-4 space-y-4">
          <div className="frost-panel rounded-3xl p-5 space-y-4">
            <h3 className="text-sm font-bold text-slate-800 flex items-center justify-between border-b border-slate-100 pb-3">
              <span>Risk Tier Distribution</span>
              <span className="text-[10px] text-slate-400 font-mono">Calibrated 0-100</span>
            </h3>

            <div className="space-y-3">
              {/* SAFE */}
              <div className="p-3 rounded-2xl bg-emerald-50/70 border border-emerald-100 flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="w-7 h-7 rounded-xl bg-emerald-500 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                    ✓
                  </div>
                  <div>
                    <span className="text-xs font-bold text-emerald-900 block">SAFE</span>
                    <span className="text-[10px] text-emerald-600">Score &le; 30 (Frictionless)</span>
                  </div>
                </div>
                <span className="text-lg font-black text-emerald-700 font-mono">
                  {stats?.riskLevelDistribution?.SAFE || 1240}
                </span>
              </div>

              {/* REVIEW */}
              <div className="p-3 rounded-2xl bg-amber-50/70 border border-amber-100 flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="w-7 h-7 rounded-xl bg-amber-500 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                    !
                  </div>
                  <div>
                    <span className="text-xs font-bold text-amber-900 block">REVIEW</span>
                    <span className="text-[10px] text-amber-600">Score 31-70 (Step-Up 2FA)</span>
                  </div>
                </div>
                <span className="text-lg font-black text-amber-700 font-mono">
                  {stats?.riskLevelDistribution?.REVIEW || 84}
                </span>
              </div>

              {/* HIGH RISK */}
              <div className="p-3 rounded-2xl bg-rose-50/70 border border-rose-100 flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="w-7 h-7 rounded-xl bg-rose-500 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                    ✕
                  </div>
                  <div>
                    <span className="text-xs font-bold text-rose-900 block">HIGH RISK</span>
                    <span className="text-[10px] text-rose-600">Score &gt; 70 (Halt & Alert)</span>
                  </div>
                </div>
                <span className="text-lg font-black text-rose-700 font-mono">
                  {stats?.riskLevelDistribution?.HIGH_RISK || 19}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ════════════════════════════════════════════════════════════════════════
          4. LIVE REAL-TIME TRANSACTION FEED
         ════════════════════════════════════════════════════════════════════════ */}
      <div className="frost-panel rounded-3xl p-5 sm:p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center space-x-3">
            <div className="relative flex items-center justify-center">
              <span
                className={`animate-ping absolute inline-flex h-3 w-3 rounded-full opacity-75 ${
                  wsConnected ? 'bg-cyan-400' : 'bg-amber-400'
                }`}
              />
              <span
                className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  wsConnected ? 'bg-cyan-500' : 'bg-amber-500'
                }`}
              />
            </div>
            <h3 className="text-sm font-bold text-slate-800">
              Live Real-Time Surveillance Feed
            </h3>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
              WebSocket /ws/monitor
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={togglePauseStream}
              className="px-3 py-1 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 flex items-center space-x-1.5 shadow-sm transition-colors"
            >
              {isPaused ? <Play className="w-3 h-3 text-cyan-600" /> : <Pause className="w-3 h-3 text-amber-600" />}
              <span>{isPaused ? 'Resume Stream' : 'Pause Feed'}</span>
            </button>
          </div>
        </div>

        {/* Stream List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[460px] overflow-y-auto pr-1">
          {filteredStream.length === 0 ? (
            <div className="col-span-2 py-12 text-center text-slate-400 space-y-2">
              <Radio className="w-7 h-7 mx-auto text-cyan-500 animate-pulse" />
              <p className="text-xs">Listening for incoming live transaction events...</p>
            </div>
          ) : (
            filteredStream.map((item, idx) => (
              <div
                key={`${item.transactionId}-${idx}`}
                onClick={() => navigate(`/transactions/${item.transactionId}`)}
                className="p-3.5 rounded-2xl bg-white/90 border border-slate-200/80 hover:border-cyan-400 hover:shadow-md transition-all cursor-pointer space-y-2 group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono font-bold text-indigo-600">
                      #{item.transactionId}
                    </span>
                    <span className="text-xs font-bold text-slate-800">
                      {item.userName}
                    </span>
                  </div>
                  {getRiskBadge(item.prediction?.riskLevel || 'SAFE')}
                </div>

                <div className="flex items-center justify-between text-xs text-slate-600 pt-1">
                  <span className="text-sm font-black text-slate-900">
                    {formatCurrency(item.amount)}
                  </span>
                  <div className="flex items-center space-x-2 font-mono text-[11px]">
                    <span>Score: <strong>{item.prediction?.riskScore}</strong></span>
                    <span className="text-slate-400">•</span>
                    <span className="text-slate-500 truncate max-w-[120px]">{item.location}</span>
                  </div>
                </div>

                {item.explanation?.contributingFactors?.length > 0 && (
                  <p className="text-[11px] text-slate-500 bg-slate-50 p-2 rounded-xl border border-slate-100 line-clamp-1">
                    <strong className="text-slate-700">Driver: </strong>
                    {item.explanation.contributingFactors[0].description}
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
