/**
 * RiskBadge.tsx - Reusable badge component for risk tiers.
 */

import React from 'react';
import type { RiskTier } from '../types';
import { getRiskTierStyles } from '../utils/formatters';

interface RiskBadgeProps {
  tier: RiskTier;
  size?: 'sm' | 'md' | 'lg';
  showDot?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  tier,
  size = 'md',
  showDot = true,
}) => {
  const styles = getRiskTierStyles(tier);

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  };

  const dotClasses = {
    HIGH: 'bg-red-500',
    MODERATE: 'bg-amber-500',
    LOW: 'bg-emerald-500',
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${styles.bg} ${styles.text} ${styles.border} ${sizeClasses[size]}`}
    >
      {showDot && (
        <span
          className={`w-1.5 h-1.5 rounded-full mr-1.5 ${dotClasses[tier] || 'bg-slate-400'}`}
        />
      )}
      {styles.label}
    </span>
  );
};
