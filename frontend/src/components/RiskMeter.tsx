/**
 * RiskMeter.tsx - Visual gauge representing calibrated fraud probability with frosted aesthetic.
 */

import React from 'react';
import type { RiskTier } from '../types';

interface RiskMeterProps {
  percentage: number;
  tier: RiskTier;
  size?: number;
}

export const RiskMeter: React.FC<RiskMeterProps> = ({
  percentage,
  tier,
  size = 200,
}) => {
  // Clamp percentage between 0 and 100
  const clamped = Math.max(0, Math.min(100, percentage));

  // Determine color based on tier
  const colorMap = {
    LOW: { stroke: '#10b981', text: 'text-emerald-600', label: 'Low Risk' },
    MODERATE: { stroke: '#f59e0b', text: 'text-amber-600', label: 'Moderate Risk' },
    HIGH: { stroke: '#ef4444', text: 'text-rose-600', label: 'High Risk' },
  };

  const { stroke, text, label } = colorMap[tier] || colorMap.LOW;

  // Arc calculation for semi-circle
  const radius = size * 0.4;
  const strokeWidth = size * 0.08;
  const center = size / 2;
  const circumference = Math.PI * radius; // Half-circle perimeter
  const strokeDashoffset = circumference - (clamped / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center relative">
      <svg
        width={size}
        height={size * 0.65}
        viewBox={`0 0 ${size} ${size * 0.7}`}
        className="overflow-visible"
      >
        <defs>
          <linearGradient id="meterGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="50%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#ef4444" />
          </linearGradient>
        </defs>

        {/* Background Track Arc */}
        <path
          d={`M ${center - radius} ${center} A ${radius} ${radius} 0 0 1 ${center + radius} ${center}`}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Active Probability Stroke Arc */}
        <path
          d={`M ${center - radius} ${center} A ${radius} ${radius} 0 0 1 ${center + radius} ${center}`}
          fill="none"
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className="transition-all duration-700 ease-out"
        />

        {/* Needle Tick Indicators at thresholds (35% and 70%) */}
        <circle cx={center - radius * Math.cos(Math.PI * 0.35)} cy={center - radius * Math.sin(Math.PI * 0.35)} r="3" fill="#94a3b8" />
        <circle cx={center - radius * Math.cos(Math.PI * 0.70)} cy={center - radius * Math.sin(Math.PI * 0.70)} r="3" fill="#94a3b8" />
      </svg>

      {/* Center Value */}
      <div className="text-center -mt-8">
        <span className={`text-4xl font-black tracking-tight ${text}`}>
          {clamped.toFixed(1)}%
        </span>
        <div className="text-xs uppercase tracking-wider font-bold text-slate-700 mt-0.5">
          {label}
        </div>
        <div className="text-[11px] text-slate-500 font-mono">
          Calibrated Risk Score
        </div>
      </div>
    </div>
  );
};
