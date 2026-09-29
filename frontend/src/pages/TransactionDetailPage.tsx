/**
 * TransactionDetailPage.tsx - Deep inspection of a specific transaction including
 * prediction breakdown, receiver profile, behavioral telemetry, and explainability factors.
 * Styled with the cyber-pastel frosted glass design system.
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  AlertTriangle,
  ShieldAlert,
  Smartphone,
  MapPin,
  Activity,
  Zap,
  Radio,
  Sliders,
  Bell,
  ArrowUpRight,
  Info,
  CheckCircle2
} from 'lucide-react';
import { apiService } from '../services/api';
import type { PayGuardTransactionDetail } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';

export const TransactionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [tx, setTx] = useState<PayGuardTransactionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiService.getTransactionById(id);
        setTx(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Transaction not found.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id]);

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !tx) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate('/transactions')}
          className="flex items-center text-xs font-bold text-indigo-600 hover:underline"
        >
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back to Transactions
        </button>
        <ErrorAlert message={error || 'Transaction not found'} />
      </div>
    );
  }

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'SAFE':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-4 h-4 mr-1.5" /> SAFE (Score &le; 30)
          </span>
        );
      case 'REVIEW':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="w-4 h-4 mr-1.5" /> REVIEW (Score 31-70)
          </span>
        );
      case 'HIGH RISK':
      default:
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 shadow-sm">
            <ShieldAlert className="w-4 h-4 mr-1.5" /> HIGH RISK (Score &gt; 70)
          </span>
        );
    }
  };

  const getRiskMeterColor = (score: number) => {
    if (score <= 30) return 'from-emerald-500 to-teal-400';
    if (score <= 70) return 'from-amber-500 to-orange-400';
    return 'from-rose-500 to-pink-600';
  };

  return (
    <div className="space-y-6">
      {/* Top Bar with Back Button & Badges */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200/80 pb-5">
        <div>
          <button
            onClick={() => navigate('/transactions')}
            className="flex items-center text-xs font-bold text-indigo-600 hover:text-indigo-800 transition-colors mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1" />
            <span>Back to Transactions</span>
          </button>
          <div className="flex items-center space-x-3">
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              Transaction #{tx.transactionId}
            </h2>
            <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
              {tx.status}
            </span>
          </div>
          <span className="text-xs text-slate-400 mt-1 block">
            Processed at {formatDate(tx.timestamp)}
          </span>
        </div>

        <div className="flex items-center space-x-3">
          {getRiskBadge(tx.prediction.riskLevel)}
        </div>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Transaction Metadata & Multi-Vector Breakdown (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Core Transaction Card */}
          <div className="frost-panel rounded-3xl p-6 space-y-5 border border-white/80">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Zap className="w-4 h-4 text-indigo-600" />
              <span>Payment Details</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
                <span className="text-xs font-bold text-slate-500 block mb-1">Transfer Amount</span>
                <span className="text-2xl font-black text-slate-900">
                  {formatCurrency(tx.amount)}
                </span>
                <span className="text-[11px] text-slate-400 block mt-1">
                  Method: {tx.paymentMethod}
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
                <span className="text-xs font-bold text-slate-500 block mb-1">Sender Account</span>
                <div className="flex items-center space-x-1.5">
                  <span className="text-sm font-bold text-slate-900">{tx.userName}</span>
                  <button
                    onClick={() => navigate(`/profile/${tx.userId}`)}
                    className="text-xs text-indigo-600 font-bold hover:underline flex items-center ml-1"
                  >
                    (Profile <ArrowUpRight className="w-3 h-3 ml-0.5" />)
                  </button>
                </div>
                <span className="text-[11px] text-slate-500 font-mono block mt-1">
                  {tx.userEmail}
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
                <span className="text-xs font-bold text-slate-500 block mb-1">Telemetry Location</span>
                <span className="text-sm font-bold text-slate-800 flex items-center space-x-1.5">
                  <MapPin className="w-3.5 h-3.5 text-indigo-600" />
                  <span>{tx.location}</span>
                </span>
                <span className="text-[11px] text-slate-500 block mt-1">
                  {tx.behavioralAnalysis.isNewLocation ? (
                    <span className="text-amber-700 font-semibold">⚠️ New location for this user</span>
                  ) : (
                    <span className="text-emerald-700 font-semibold">✓ Known primary location</span>
                  )}
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
                <span className="text-xs font-bold text-slate-500 block mb-1">Device Fingerprint</span>
                <span className="text-sm font-bold text-slate-800 flex items-center space-x-1.5">
                  <Smartphone className="w-3.5 h-3.5 text-indigo-600" />
                  <span className="truncate">{tx.deviceType}</span>
                </span>
                <span className="text-[11px] text-slate-500 block mt-1">
                  {tx.behavioralAnalysis.isNewDevice ? (
                    <span className="text-amber-700 font-semibold">⚠️ Unrecognized device</span>
                  ) : (
                    <span className="text-emerald-700 font-semibold">✓ Recognized trusted device</span>
                  )}
                </span>
              </div>
            </div>
          </div>

          {/* Receiver Analysis Card */}
          <div className="frost-panel rounded-3xl p-6 space-y-4 border border-white/80">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Radio className="w-4 h-4 text-purple-600" />
              <span>Receiver Reputation & Risk Analysis</span>
            </h3>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
              <div>
                <span className="text-xs font-bold text-slate-500 block">Receiver UPI Address</span>
                <span className="text-sm font-mono font-bold text-slate-900 mt-0.5 block">
                  {tx.receiverProfile.receiverAddress}
                </span>
              </div>

              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <span className="text-xs font-bold text-slate-500 block">Reputation</span>
                  <span className="text-sm font-black text-emerald-600">
                    {tx.receiverProfile.receiverReputationScore} / 100
                  </span>
                </div>
                <div className="text-right border-l border-slate-200 pl-4">
                  <span className="text-xs font-bold text-slate-500 block">Risk Rating</span>
                  <span className={`text-sm font-black ${
                    tx.receiverProfile.receiverRiskRating > 50 ? 'text-rose-600' : 'text-slate-700'
                  }`}>
                    {tx.receiverProfile.receiverRiskRating} / 100
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Behavioral Analysis Vector Card */}
          <div className="frost-panel rounded-3xl p-6 space-y-4 border border-white/80">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Sliders className="w-4 h-4 text-emerald-600" />
              <span>Behavioral Profile Baseline Comparison</span>
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                  User Avg Spend
                </span>
                <span className="text-sm font-black text-slate-900 mt-1 block">
                  {formatCurrency(tx.behavioralAnalysis.userAvgAmount)}
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                  Amount Deviation
                </span>
                <span className={`text-sm font-black mt-1 block ${
                  tx.behavioralAnalysis.amountDeviation > 2.0 ? 'text-amber-600' : 'text-slate-800'
                }`}>
                  {tx.behavioralAnalysis.amountDeviation}x
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                  1h Velocity
                </span>
                <span className={`text-sm font-black mt-1 block ${
                  tx.behavioralAnalysis.transactionVelocity >= 3 ? 'text-rose-600' : 'text-slate-800'
                }`}>
                  {tx.behavioralAnalysis.transactionVelocity} txns
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                  Behavioral Score
                </span>
                <span className="text-sm font-black text-indigo-600 mt-1 block">
                  {tx.behavioralAnalysis.behavioralRiskScore} / 100
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Prediction Engine & Explainability (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Overall Risk Score Meter */}
          <div className="frost-panel rounded-3xl p-6 space-y-5 border border-white/80">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Activity className="w-4 h-4 text-indigo-600" />
              <span>Multi-Vector Composite Score</span>
            </h3>

            <div className="text-center py-4 space-y-2">
              <span className="text-6xl font-black text-slate-900 tracking-tight">
                {tx.prediction.riskScore}
              </span>
              <span className="text-xs text-slate-500 font-semibold block">Composite Risk Metric (0-100)</span>

              {/* Progress meter bar */}
              <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden mt-3 p-0.5 border border-slate-200">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${getRiskMeterColor(tx.prediction.riskScore)} transition-all duration-700 shadow-sm`}
                  style={{ width: `${Math.min(100, Math.max(5, tx.prediction.riskScore))}%` }}
                />
              </div>

              <div className="flex justify-between text-[10px] text-slate-400 font-mono font-bold pt-1">
                <span>0 SAFE</span>
                <span>30</span>
                <span>70 REVIEW</span>
                <span>100 HIGH</span>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Machine Learning Fraud Prob:</span>
                <strong className="text-slate-900 font-bold">{(tx.prediction.fraudProbability * 100).toFixed(1)}%</strong>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Behavioral Risk Contribution (30%):</span>
                <strong className="text-slate-900 font-bold">{tx.behavioralAnalysis.behavioralRiskScore}</strong>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Receiver Risk Contribution (20%):</span>
                <strong className="text-slate-900 font-bold">{tx.receiverProfile.receiverRiskRating}</strong>
              </div>
            </div>
          </div>

          {/* Explainability Breakdown Card */}
          <div className="frost-panel rounded-3xl p-6 space-y-4 border border-white/80">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Info className="w-4 h-4 text-cyan-600" />
              <span>Explainable AI Attribution</span>
            </h3>

            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              {tx.explanation.summary}
            </p>

            <div className="space-y-2.5 pt-2">
              <span className="text-[11px] uppercase tracking-wider text-slate-400 font-bold block">
                Top Contributing Indicators:
              </span>

              {tx.explanation.contributingFactors?.map((factor, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-1"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-800">{factor.label}</span>
                    <span className="text-[10px] font-mono font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-200">
                      Impact: {(factor.importance * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    {factor.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Alert Box (if present) */}
          {tx.alerts && tx.alerts.length > 0 && (
            <div className="bg-rose-50 border border-rose-200 rounded-3xl p-5 space-y-3">
              <div className="flex items-center space-x-2 text-rose-700 font-extrabold text-xs tracking-wider uppercase">
                <Bell className="w-4 h-4 text-rose-600" />
                <span>FRAUD ALERT GENERATED</span>
              </div>
              {tx.alerts.map((al) => (
                <div key={al.alertId} className="text-xs text-slate-700 space-y-1">
                  <div>
                    <span className="text-slate-500">Alert ID:</span> #{al.alertId} •{' '}
                    <strong className="text-rose-700">{al.alertType}</strong>
                  </div>
                  <div>
                    <span className="text-slate-500">Severity:</span> {al.alertSeverity} •{' '}
                    <span className="text-slate-500">Status:</span> {al.status}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
