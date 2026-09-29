/**
 * PasswordInput.tsx - Controlled password field with visibility toggle and strength feedback.
 * Uses strict descriptive naming (isPasswordVisible, handleTogglePasswordVisibility).
 */

import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface PasswordInputProps {
  id: string;
  value: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  autoComplete?: string;
}

export const PasswordInput: React.FC<PasswordInputProps> = ({
  id,
  value,
  onChange,
  placeholder = '••••••••',
  disabled = false,
  required = true,
  autoComplete = 'current-password',
}) => {
  const [isPasswordVisible, setIsPasswordVisible] = useState<boolean>(false);

  const handleTogglePasswordVisibility = () => {
    setIsPasswordVisible((previousState) => !previousState);
  };

  return (
    <div className="relative">
      <input
        id={id}
        name="password"
        type={isPasswordVisible ? 'text' : 'password'}
        value={value}
        onChange={onChange}
        disabled={disabled}
        required={required}
        placeholder={placeholder}
        autoComplete={autoComplete}
        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all pr-10 shadow-sm"
      />

      <button
        type="button"
        tabIndex={-1}
        onClick={handleTogglePasswordVisibility}
        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 transition-colors focus:outline-none"
        title={isPasswordVisible ? 'Hide password' : 'Show password'}
      >
        {isPasswordVisible ? (
          <EyeOff className="w-4 h-4 text-indigo-600" />
        ) : (
          <Eye className="w-4 h-4 text-slate-400" />
        )}
      </button>
    </div>
  );
};
