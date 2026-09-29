/**
 * RiskFactorsList.tsx - Visual explainability breakdown of top risk drivers with frosted cards.
 */

import React from 'react';
import type { RiskFactorExplanation } from '../types';
import { AlertCircle, ShieldCheck } from 'lucide-react';

interface RiskFactorsListProps {
  factors: RiskFactorExplanation[];
}

export const RiskFactorsList: React.FC<RiskFactorsListProps> = ({ factors }) => {
  if (!factors || factors.length === 0) {
    return (
      <div className="text-xs text-slate-500 italic py-2">
        No anomalous behavioral factors observed.
      </div>
    );
  }

  // Find max absolute impact to normalize bar width
  const maxImpact = Math.max(...factors.map((f) => Math.abs(f.impact_score)), 0.05);

  return (
    <div className="space-y-3">
      {factors.map((factor, index) => {
        const isRisk = factor.impact_score > 0.05;
        const barWidth = Math.min(100, Math.max(12, (Math.abs(factor.impact_score) / maxImpact) * 100));

        return (
          <div
            key={`${factor.feature}-${index}`}
            className="p-3.5 rounded-xl bg-white/90 border border-slate-200/80 hover:border-slate-300 transition-all shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {isRisk ? (
                  <AlertCircle className="w-4 h-4 text-rose-500 shrink-0" />
                ) : (
                  <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0" />
                )}
                <span className="text-sm font-bold text-slate-800">
                  {factor.label || factor.feature}
                </span>
                <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono font-semibold">
                  {factor.category}
                </span>
              </div>
              <div className="text-right">
                <span
                  className={`text-xs font-mono font-bold ${
                    isRisk ? 'text-rose-600' : 'text-emerald-600'
                  }`}
                >
                  {isRisk ? '+' : ''}
                  {factor.impact_score.toFixed(3)} impact
                </span>
              </div>
            </div>

            {/* Impact Bar */}
            <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-2.5">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  isRisk ? 'bg-gradient-to-r from-amber-400 to-rose-500' : 'bg-emerald-500'
                }`}
                style={{ width: `${barWidth}%` }}
              />
            </div>

            <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
              {factor.description || 'Behavioral telemetry factor impacting risk classification.'}
            </p>
          </div>
        );
      })}
    </div>
  );
};
