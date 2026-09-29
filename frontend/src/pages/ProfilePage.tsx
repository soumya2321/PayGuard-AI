/**
 * ProfilePage.tsx - Deep inspection of a user's BEHAVIOR_PROFILE:
 * baseline normal patterns vs. flagged deviations.
 * Redesigned with Cyber-Pastel Frosted Glass aesthetic matching the console reference image.
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Sliders,
  ShieldCheck,
  AlertTriangle,
  ShieldAlert,
  ArrowRight,
  ArrowLeft,
  Smartphone,
  MapPin,
  TrendingUp,
} from 'lucide-react';
import { apiService } from '../services/api';
import type { PayGuardUserProfile, PayGuardUserItem } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';

export const ProfilePage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();

  const [profile, setProfile] = useState<PayGuardUserProfile | null>(null);
  const [allUsers, setAllUsers] = useState<PayGuardUserItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async (targetId: string | number) => {
    setLoading(true);
    setError(null);
    try {
      const [profileData, usersData] = await Promise.all([
        apiService.getUserProfile(targetId),
        apiService.getUsers(),
      ]);
      setProfile(profileData);
      setAllUsers(usersData);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch user behavior profile.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchProfile(userId);
    }
  }, [userId]);

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate('/transactions')}
          className="flex items-center text-xs text-indigo-600 font-semibold hover:underline"
        >
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back to Transactions
        </button>
        <ErrorAlert message={error || 'User profile not found.'} />
      </div>
    );
  }

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'SAFE':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <ShieldCheck className="w-3 h-3 mr-1 text-emerald-600" /> SAFE
          </span>
        );
      case 'REVIEW':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" /> REVIEW
          </span>
        );
      case 'HIGH RISK':
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
            <ShieldAlert className="w-3 h-3 mr-1 text-rose-600" /> HIGH RISK
          </span>
        );
    }
  };

  return (
    <div className="space-y-7">
      {/* Header & Quick User Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200/80 pb-5">
        <div>
          <button
            onClick={() => navigate('/transactions')}
            className="flex items-center text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1" />
            <span>Back to Transactions</span>
          </button>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              {profile.name}
            </h1>
            <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
              User ID #{profile.userId}
            </span>
          </div>
          <span className="text-xs text-slate-500 font-mono mt-1 block">
            {profile.email} • Enrolled {formatDate(profile.createdAt)}
          </span>
        </div>

        {/* User Switcher Dropdown */}
        <div className="flex items-center space-x-3">
          <span className="text-xs font-semibold text-slate-500">Switch Profile:</span>
          <select
            value={profile.userId}
            onChange={(e) => navigate(`/profile/${e.target.value}`)}
            className="px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-800 shadow-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          >
            {allUsers.map((u) => (
              <option key={u.userId} value={u.userId}>
                {u.name} (#{u.userId})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Grid: Baseline Profile (5 cols) + Flagged Deviations (7 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-7 items-start">
        {/* Left Column: Baseline Behavior Profile (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="frost-panel rounded-2xl border border-white/80 p-6 shadow-sm space-y-5">
            <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-200/80 pb-3">
              <Sliders className="w-4 h-4 text-indigo-600" />
              <span>Behavioral Baseline</span>
            </h2>

            <p className="text-xs text-slate-500 leading-relaxed">
              Standard telemetry footprint established from verified historical activity.
            </p>

            <div className="space-y-3">
              <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 block mb-0.5">Average Spend Size</span>
                <span className="text-xl font-black text-slate-900">
                  {formatCurrency(profile.avgTransactionAmount)}
                </span>
                <span className="text-[11px] text-slate-400 block mt-0.5">
                  Typical transfer baseline
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 block mb-0.5">Daily Velocity Target</span>
                <span className="text-lg font-bold text-slate-800">
                  {profile.avgTransactionFrequency} transfers / day
                </span>
                <span className="text-[11px] text-slate-400 block mt-0.5">
                  Frequency expectation
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 block mb-1">Primary Geographic Footprint</span>
                <span className="text-sm font-bold text-slate-800 flex items-center space-x-1.5">
                  <MapPin className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                  <span>{profile.primaryLocations}</span>
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 block mb-1">Recognized Device Patterns</span>
                <span className="text-sm font-bold text-slate-800 flex items-center space-x-1.5">
                  <Smartphone className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                  <span>{profile.deviceUsePatterns}</span>
                </span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-200/80 text-[11px] text-slate-400 font-mono">
              Profile last updated: {formatDate(profile.lastUpdate)}
            </div>
          </div>

          {/* Account Risk Summary Card */}
          <div className="frost-panel rounded-2xl border border-white/80 p-6 shadow-sm space-y-4">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              <span>Historical Risk Summary</span>
            </h2>

            <div className="grid grid-cols-2 gap-3 text-center">
              <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 block">Total Transactions</span>
                <span className="text-2xl font-black text-slate-900 mt-1 block">
                  {profile.totalUserTransactions}
                </span>
              </div>
              <div className="p-3.5 rounded-xl bg-white border border-amber-200/80 shadow-sm">
                <span className="text-xs font-semibold text-amber-700 block">Flagged / Anomalies</span>
                <span className="text-2xl font-black text-amber-600 mt-1 block">
                  {profile.flaggedUserTransactions}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Flagged Deviations vs Normal Patterns (7 cols) */}
        <div className="lg:col-span-7 frost-panel rounded-2xl border border-white/80 p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
            <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <span>Observed Activity & Flagged Deviations</span>
            </h2>
            <span className="text-xs text-slate-500 font-mono font-semibold px-2 py-0.5 rounded bg-slate-100">
              Recent Transfers
            </span>
          </div>

          <p className="text-xs text-slate-500">
            Transactions evaluated against {profile.name}’s baseline (₹{profile.avgTransactionAmount} avg). High amount deviation or unknown device triggers step-up review or fraud alarms.
          </p>

          <div className="space-y-3">
            {profile.recentUserTransactions.length === 0 ? (
              <div className="py-12 text-center text-slate-400">
                No transactions recorded for this profile yet.
              </div>
            ) : (
              profile.recentUserTransactions.map((tx) => (
                <div
                  key={tx.transactionId}
                  onClick={() => navigate(`/transactions/${tx.transactionId}`)}
                  className="p-4 rounded-xl bg-white border border-slate-200/80 hover:border-indigo-400 hover:shadow-md transition-all cursor-pointer group space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono text-indigo-600 font-bold">
                        #{tx.transactionId}
                      </span>
                      <span className="text-sm font-black text-slate-900">
                        {formatCurrency(tx.amount)}
                      </span>
                      <span className="text-xs text-slate-500 font-mono">
                        → {tx.receiverAddress}
                      </span>
                    </div>
                    {getRiskBadge(tx.riskLevel)}
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs pt-1.5 border-t border-slate-100">
                    <div>
                      <span className="text-slate-500 block text-[10px] font-semibold">Deviation vs Mean:</span>
                      <span className={`font-bold ${tx.amountDeviation > 2.0 ? 'text-amber-600' : 'text-slate-700'}`}>
                        {tx.amountDeviation}x average
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-500 block text-[10px] font-semibold">Location:</span>
                      <span className="text-slate-700 font-medium truncate block">{tx.location}</span>
                    </div>

                    <div>
                      <span className="text-slate-500 block text-[10px] font-semibold">Risk Score:</span>
                      <span className="text-slate-900 font-black">{tx.riskScore} / 100</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                    <span>{formatDate(tx.timestamp)}</span>
                    <span className="text-indigo-600 font-bold group-hover:translate-x-0.5 transition-transform flex items-center">
                      Inspect Evidence <ArrowRight className="w-3 h-3 ml-1" />
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
