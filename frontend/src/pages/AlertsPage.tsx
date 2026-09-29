/**
 * AlertsPage.tsx - High-risk transaction alerts queue with severity filtering,
 * status filtering, and analyst disposition actions (Mark Reviewed / Resolved).
 * Styled with the cyber-pastel frosted glass design system.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  AlertTriangle,
  ShieldAlert,
  CheckCircle,
  Filter,
  ArrowRight,
  RotateCcw,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { apiService } from '../services/api';
import type { PayGuardAlertItem } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';

export const AlertsPage: React.FC = () => {
  const navigate = useNavigate();

  const [alerts, setAlerts] = useState<PayGuardAlertItem[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getAlerts({
        status: statusFilter,
        severity: severityFilter,
        limit: 100,
      });
      setAlerts(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alerts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, severityFilter]);

  const handleUpdateStatus = async (alertId: number, newStatus: string) => {
    try {
      await apiService.updateAlert(alertId, newStatus);
      setActionSuccess(`Alert #${alertId} marked as ${newStatus}`);
      setTimeout(() => setActionSuccess(null), 3000);
      fetchAlerts();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update alert status.');
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'CRITICAL':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
            <ShieldAlert className="w-3 h-3 mr-1" /> CRITICAL
          </span>
        );
      case 'HIGH':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="w-3 h-3 mr-1" /> HIGH
          </span>
        );
      case 'MEDIUM':
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            MEDIUM
          </span>
        );
    }
  };

  const getStatusBadge = (st: string) => {
    switch (st.toUpperCase()) {
      case 'PENDING':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <Clock className="w-3 h-3 mr-1" /> PENDING
          </span>
        );
      case 'REVIEWED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <CheckCircle className="w-3 h-3 mr-1" /> REVIEWED
          </span>
        );
      case 'RESOLVED':
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 mr-1" /> RESOLVED
          </span>
        );
    }
  };

  const pendingCount = alerts.filter((a) => a.status === 'PENDING').length;
  const criticalCount = alerts.filter((a) => a.alertSeverity === 'CRITICAL').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-rose-600 text-xs font-bold uppercase tracking-wider">
            <Bell className="w-4 h-4 text-rose-500" />
            <span>Fraud Incident Escalations</span>
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight mt-0.5">
            Fraud Alerts Incident Queue
          </h2>
          <p className="text-slate-500 text-xs">
            Review flagged high-risk anomalies, inspect telemetry evidence, and assign analyst resolutions.
          </p>
        </div>

        <button
          onClick={fetchAlerts}
          className="self-start sm:self-auto p-2.5 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors shadow-sm"
          title="Refresh Alerts"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {actionSuccess && (
        <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold flex items-center space-x-2 shadow-sm animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {error && <ErrorAlert message={error} />}

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="frost-panel rounded-3xl p-5 border border-white/80">
          <span className="text-xs font-bold text-slate-500 block">Total Alerts in Queue</span>
          <span className="text-3xl font-black text-slate-900 mt-2 block">{alerts.length}</span>
          <span className="text-[11px] text-slate-400 mt-1 block">Active incident ledger</span>
        </div>
        <div className="frost-panel rounded-3xl p-5 border border-white/80">
          <span className="text-xs font-bold text-slate-500 block">Pending Action</span>
          <span className="text-3xl font-black text-amber-600 mt-2 block">{pendingCount}</span>
          <span className="text-[11px] text-amber-700/80 mt-1 block">Requires analyst review</span>
        </div>
        <div className="frost-panel rounded-3xl p-5 border border-white/80">
          <span className="text-xs font-bold text-slate-500 block">Critical Severity</span>
          <span className="text-3xl font-black text-rose-600 mt-2 block">{criticalCount}</span>
          <span className="text-[11px] text-rose-700/80 mt-1 block">Immediate block applied</span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="frost-panel rounded-3xl p-4.5 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-white/80">
        {/* Status Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <span className="text-xs font-bold text-slate-500 mr-1">Status:</span>
          {['ALL', 'PENDING', 'REVIEWED', 'RESOLVED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                statusFilter === st
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-sm'
                  : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200 shadow-sm'
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        {/* Severity Filter */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold text-slate-500 mr-1">Severity:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                severityFilter === sev
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200 shadow-sm'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Table */}
      <div className="frost-panel rounded-3xl overflow-hidden shadow-sm border border-white/80">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/70 text-slate-500 text-[11px] font-bold uppercase tracking-wider">
                <th className="py-3.5 px-4">Alert ID</th>
                <th className="py-3.5 px-4">Alert Type</th>
                <th className="py-3.5 px-4">Severity</th>
                <th className="py-3.5 px-4">User & TX</th>
                <th className="py-3.5 px-4">Amount</th>
                <th className="py-3.5 px-4">Risk Score</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Timestamp</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-16 text-center">
                    <LoadingSpinner />
                  </td>
                </tr>
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400 text-xs">
                    No fraud alerts found matching the active filters.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr
                    key={alert.alertId}
                    className="hover:bg-slate-50/80 transition-colors group"
                  >
                    <td className="py-3.5 px-4 font-mono text-xs text-rose-600 font-bold">
                      #{alert.alertId}
                    </td>

                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      <span className="font-mono text-xs">
                        {alert.alertType}
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      {getSeverityBadge(alert.alertSeverity)}
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-800">{alert.userName}</div>
                      <div
                        onClick={() => navigate(`/transactions/${alert.transactionId}`)}
                        className="text-[11px] font-mono text-indigo-600 hover:underline cursor-pointer flex items-center"
                      >
                        TX #{alert.transactionId} <ArrowRight className="w-2.5 h-2.5 ml-0.5" />
                      </div>
                    </td>

                    <td className="py-3.5 px-4 font-black text-slate-900">
                      {formatCurrency(alert.amount)}
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="font-black text-rose-600 text-xs">{alert.riskScore}</span>
                      <span className="text-[10px] text-slate-400 font-mono block">
                        ML {(alert.fraudProbability * 100).toFixed(0)}%
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      {getStatusBadge(alert.status)}
                    </td>

                    <td className="py-3.5 px-4 text-xs text-slate-400 font-medium">
                      {formatDate(alert.alertTimestamp)}
                    </td>

                    <td className="py-3.5 px-4 text-right space-x-2">
                      {alert.status === 'PENDING' && (
                        <button
                          onClick={() => handleUpdateStatus(alert.alertId, 'REVIEWED')}
                          className="px-2.5 py-1 text-xs font-bold rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 transition-colors shadow-sm"
                        >
                          Reviewed
                        </button>
                      )}

                      {alert.status !== 'RESOLVED' && (
                        <button
                          onClick={() => handleUpdateStatus(alert.alertId, 'RESOLVED')}
                          className="px-2.5 py-1 text-xs font-bold rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 transition-colors shadow-sm"
                        >
                          Resolve
                        </button>
                      )}

                      <button
                        onClick={() => navigate(`/transactions/${alert.transactionId}`)}
                        className="px-2.5 py-1 text-xs font-bold rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 transition-colors shadow-sm"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
