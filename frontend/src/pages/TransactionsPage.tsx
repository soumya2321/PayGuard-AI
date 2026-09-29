/**
 * TransactionsPage.tsx - Paginated, filterable transaction history table
 * with risk badges and click-through to full transaction detail.
 * Styled with the cyber-pastel frosted glass design system.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ReceiptText,
  Search,
  Filter,
  ArrowRight,
  AlertTriangle,
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  UserCheck,
  CheckCircle2
} from 'lucide-react';
import { apiService } from '../services/api';
import type { PayGuardTransactionItem, RiskLevel } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';

export const TransactionsPage: React.FC = () => {
  const navigate = useNavigate();

  const [transactions, setTransactions] = useState<PayGuardTransactionItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(15);
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getTransactions({
        limit,
        offset: page * limit,
        risk_level: riskFilter !== 'ALL' ? riskFilter : undefined,
        search: search.trim() ? search.trim() : undefined,
      });
      setTransactions(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load transaction audit ledger.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [page, riskFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0);
    fetchTransactions();
  };

  const getRiskBadge = (level: RiskLevel) => {
    switch (level) {
      case 'SAFE':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 mr-1" /> SAFE
          </span>
        );
      case 'REVIEW':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="w-3 h-3 mr-1" /> REVIEW
          </span>
        );
      case 'HIGH RISK':
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200 shadow-sm">
            <ShieldAlert className="w-3 h-3 mr-1" /> HIGH RISK
          </span>
        );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="text-[11px] font-mono font-bold text-emerald-600">COMPLETED</span>;
      case 'FLAGGED':
        return <span className="text-[11px] font-mono font-bold text-amber-600">FLAGGED</span>;
      case 'BLOCKED':
        return <span className="text-[11px] font-mono font-bold text-rose-600">BLOCKED</span>;
      default:
        return <span className="text-[11px] font-mono text-slate-500">{status}</span>;
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-600 text-xs font-bold uppercase tracking-wider">
            <ReceiptText className="w-4 h-4 text-cyan-500" />
            <span>Audit & Verification Ledger</span>
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight mt-0.5">
            Transaction History
          </h2>
          <p className="text-slate-500 text-xs">
            Search, filter, and inspect processed UPI transfers, risk scores, and telemetry evidence.
          </p>
        </div>

        <button
          onClick={fetchTransactions}
          className="self-start sm:self-auto p-2.5 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors shadow-sm"
          title="Refresh Data"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {error && <ErrorAlert message={error} />}

      {/* Filter and Search Bar */}
      <div className="frost-panel rounded-3xl p-4.5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="flex-1 relative">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by user name, location, device, or receiver UPI ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-white border border-slate-200 focus:border-indigo-500 focus:outline-none text-xs text-slate-800 placeholder-slate-400 shadow-sm"
          />
        </form>

        {/* Risk Level Filter Chips */}
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <span className="text-xs font-bold text-slate-500 mr-1">Risk:</span>
          {['ALL', 'SAFE', 'REVIEW', 'HIGH RISK'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => {
                setRiskFilter(lvl);
                setPage(0);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                riskFilter === lvl
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-sm'
                  : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200 shadow-sm'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Transactions Table */}
      <div className="frost-panel rounded-3xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/70 text-slate-500 text-[11px] font-bold uppercase tracking-wider">
                <th className="py-3.5 px-4">TX ID</th>
                <th className="py-3.5 px-4">User</th>
                <th className="py-3.5 px-4">Amount</th>
                <th className="py-3.5 px-4">Receiver</th>
                <th className="py-3.5 px-4">Location & Device</th>
                <th className="py-3.5 px-4">Risk Score</th>
                <th className="py-3.5 px-4">Classification</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-16 text-center">
                    <LoadingSpinner />
                  </td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400 text-xs">
                    No transactions match your search criteria.
                  </td>
                </tr>
              ) : (
                transactions.map((tx) => (
                  <tr
                    key={tx.transactionId}
                    className="hover:bg-slate-50/80 transition-colors group cursor-pointer"
                    onClick={() => navigate(`/transactions/${tx.transactionId}`)}
                  >
                    <td className="py-3.5 px-4 font-mono text-xs font-bold text-indigo-600">
                      #{tx.transactionId}
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-1.5">
                        <span className="font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
                          {tx.userName}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/profile/${tx.userId}`);
                          }}
                          className="text-slate-400 hover:text-indigo-600"
                          title="View User Behavior Profile"
                        >
                          <UserCheck className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      <span className="text-[11px] text-slate-400 font-medium">{formatDate(tx.timestamp)}</span>
                    </td>

                    <td className="py-3.5 px-4 font-black text-slate-900">
                      {formatCurrency(tx.amount)}
                    </td>

                    <td className="py-3.5 px-4 font-mono text-xs text-slate-600">
                      {tx.receiverAddress}
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="text-xs text-slate-700 font-semibold">{tx.location}</div>
                      <div className="text-[11px] text-slate-400 truncate max-w-[140px]">
                        {tx.deviceType}
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="font-black text-slate-900 text-xs">{tx.riskScore} / 100</div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        ML: {(tx.fraudProbability * 100).toFixed(1)}%
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      {getRiskBadge(tx.riskLevel)}
                    </td>

                    <td className="py-3.5 px-4">
                      {getStatusBadge(tx.status)}
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <span className="text-xs font-bold text-indigo-600 group-hover:translate-x-1 inline-flex items-center transition-transform">
                        Details <ArrowRight className="w-3.5 h-3.5 ml-1" />
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="border-t border-slate-100 bg-white/70 px-4 py-3 flex items-center justify-between text-xs text-slate-500">
          <div>
            Showing <strong className="text-slate-800">{transactions.length > 0 ? page * limit + 1 : 0}</strong> to{' '}
            <strong className="text-slate-800">{Math.min((page + 1) * limit, total)}</strong> of{' '}
            <strong className="text-slate-800">{total}</strong> transactions
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={() => setPage((prev) => Math.max(0, prev - 1))}
              disabled={page === 0}
              className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed shadow-sm"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 py-1 font-mono font-bold text-slate-700">
              Page {page + 1} of {Math.max(1, totalPages)}
            </span>
            <button
              onClick={() => setPage((prev) => Math.min(totalPages - 1, prev + 1))}
              disabled={page >= totalPages - 1}
              className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed shadow-sm"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
