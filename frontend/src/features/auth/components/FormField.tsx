/**
 * FormField.tsx - Reusable input wrapper component adhering to the DRY principle.
 * Standardizes labels, icons, error messages, and helper text across all forms.
 */

import React from 'react';
import { AlertCircle } from 'lucide-react';

interface FormFieldProps {
  label: string;
  htmlFor: string;
  error?: string | null;
  helpText?: string;
  icon?: React.ReactNode;
  required?: boolean;
  children: React.ReactNode;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  htmlFor,
  error,
  helpText,
  icon,
  required = false,
  children,
}) => {
  return (
    <div className="space-y-1.5 text-left">
      <div className="flex items-center justify-between">
        <label htmlFor={htmlFor} className="block text-xs font-bold text-slate-700">
          <span className="flex items-center space-x-1.5">
            {icon && <span className="text-indigo-600">{icon}</span>}
            <span>{label}</span>
            {required && <span className="text-rose-500">*</span>}
          </span>
        </label>
      </div>

      {children}

      {error ? (
        <div className="flex items-center space-x-1 text-rose-600 text-xs mt-1 font-medium">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{error}</span>
        </div>
      ) : helpText ? (
        <p className="text-[11px] text-slate-400 mt-1">{helpText}</p>
      ) : null}
    </div>
  );
};
