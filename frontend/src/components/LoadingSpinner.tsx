/**
 * LoadingSpinner.tsx - Reusable loading indicator.
 */

import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading data from server...',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-slate-400">
      <Loader2 className="w-8 h-8 animate-spin text-indigo-400 mb-3" />
      <p className="text-sm font-medium">{message}</p>
    </div>
  );
};
