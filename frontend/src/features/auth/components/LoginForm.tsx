/**
 * LoginForm.tsx - Pure UI component for credentials submission.
 * Enforces Separation of Concerns: handles local form inputs only,
 * delegates submission to parent via handleLoginSubmit without touching API or routing.
 * Styled with frosted cards and crisp typography matching the console reference image.
 */

import React, { useState } from 'react';
import { Mail, Lock, LogIn, AlertTriangle, ShieldCheck } from 'lucide-react';
import type { LoginCredentials, DemoUserAccount } from '../types/auth.types';
import { FormField } from './FormField';
import { PasswordInput } from './PasswordInput';
import { DEMO_USERS } from '../constants/demoUsers';
import { validatePasswordStrength, validateEmailAddress } from '../utils/validatePassword';

interface LoginFormProps {
  onSubmit: (credentials: LoginCredentials) => void;
  isLoading: boolean;
  errorMessage?: string | null;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSubmit,
  isLoading,
  errorMessage,
}) => {
  const [emailInput, setEmailInput] = useState<string>('');
  const [passwordInput, setPasswordInput] = useState<string>('');
  const [emailFieldError, setEmailFieldError] = useState<string | null>(null);
  const [passwordFieldError, setPasswordFieldError] = useState<string | null>(null);

  const handleLoginSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    // Reset field errors
    setEmailFieldError(null);
    setPasswordFieldError(null);

    let hasValidationError = false;

    // Validate email
    if (!emailInput.trim()) {
      setEmailFieldError('Email or UPI identifier is required.');
      hasValidationError = true;
    } else if (!validateEmailAddress(emailInput)) {
      setEmailFieldError('Please enter a valid email or UPI address.');
      hasValidationError = true;
    }

    // Validate password presence and minimum length
    if (!passwordInput) {
      setPasswordFieldError('Password is required.');
      hasValidationError = true;
    } else {
      const passwordValidation = validatePasswordStrength(passwordInput);
      if (!passwordValidation.isValid) {
        setPasswordFieldError(passwordValidation.errors[0] || 'Password does not meet security criteria.');
        hasValidationError = true;
      }
    }

    if (hasValidationError) {
      return;
    }

    // Delegate to parent callback
    onSubmit({
      email: emailInput.trim(),
      password: passwordInput,
    });
  };

  const handleSelectDemoUser = (demoUser: DemoUserAccount) => {
    setEmailInput(demoUser.email);
    setPasswordInput(demoUser.password);
    setEmailFieldError(null);
    setPasswordFieldError(null);
  };

  return (
    <div className="space-y-6">
      {/* Error alert banner */}
      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2.5 font-medium shadow-sm">
          <AlertTriangle className="w-4 h-4 shrink-0 text-rose-600" />
          <span className="leading-relaxed">{errorMessage}</span>
        </div>
      )}

      {/* Main Authentication Form */}
      <form onSubmit={handleLoginSubmit} className="space-y-4" noValidate>
        {/* Email or UPI ID Field */}
        <FormField
          label="Email or UPI Identifier"
          htmlFor="auth-email-input"
          icon={<Mail className="w-3.5 h-3.5" />}
          error={emailFieldError}
          required
        >
          <input
            id="auth-email-input"
            name="email"
            type="text"
            value={emailInput}
            onChange={(e) => {
              setEmailInput(e.target.value);
              if (emailFieldError) setEmailFieldError(null);
            }}
            disabled={isLoading}
            required
            autoComplete="username"
            placeholder="e.g. rahul.sharma@oksbi or user@example.com"
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all shadow-sm"
          />
        </FormField>

        {/* Password Field */}
        <FormField
          label="Password"
          htmlFor="auth-password-input"
          icon={<Lock className="w-3.5 h-3.5" />}
          error={passwordFieldError}
          helpText="8+ chars, 1 uppercase, 1 number, 1 special character"
          required
        >
          <PasswordInput
            id="auth-password-input"
            value={passwordInput}
            onChange={(e) => {
              setPasswordInput(e.target.value);
              if (passwordFieldError) setPasswordFieldError(null);
            }}
            disabled={isLoading}
            required
          />
        </FormField>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-600 hover:opacity-95 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-2"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              <LogIn className="w-4 h-4" />
              <span>Authenticate & Access PayGuard</span>
            </>
          )}
        </button>
      </form>

      {/* 1-Click Demo Accounts Section */}
      <div className="pt-4 border-t border-slate-200/80 space-y-2.5">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span className="font-bold flex items-center space-x-1.5 text-slate-700">
            <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />
            <span>Academic Demo Accounts (1-Click Fill)</span>
          </span>
          <span className="text-[10px] text-slate-500 font-mono font-semibold px-1.5 py-0.2 rounded bg-slate-100">Pre-seeded</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {DEMO_USERS.map((demoUser) => (
            <button
              key={demoUser.email}
              type="button"
              onClick={() => handleSelectDemoUser(demoUser)}
              disabled={isLoading}
              className="p-2.5 rounded-xl bg-white border border-slate-200 hover:border-indigo-400 hover:bg-slate-50/80 transition-all text-left flex flex-col justify-between group shadow-sm disabled:opacity-40"
            >
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 inline-block mb-1">
                  {demoUser.role}
                </span>
                <p className="text-xs font-bold text-slate-800 group-hover:text-indigo-600 transition-colors truncate">
                  {demoUser.name}
                </p>
              </div>
              <span className="text-[10px] text-slate-400 font-mono mt-1 truncate">
                {demoUser.email}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
