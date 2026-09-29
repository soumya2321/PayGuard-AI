/**
 * LoginPage.tsx - Authentication portal featuring a cinematic animated hero section.
 * Architecture:
 * - Upper Section: Premium animated holographic fintech hero featuring the uploaded phone visual.
 * - Lower Section (after scrolling): Frosted-glass identity verification and login box.
 * Official Title: PAYGUARD AI – INTELLIGENT UPI FRAUD DETECTION SYSTEM
 */

import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, Lock, Cpu, Sparkles, ArrowUp } from 'lucide-react';
import { useAuth } from './hooks/useAuth';
import { LoginForm } from './components/LoginForm';
import { HeroVisualSection } from './components/HeroVisualSection';
import type { LoginCredentials } from './types/auth.types';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const loginBoxRef = useRef<HTMLDivElement>(null);
  const { isAuthenticated, isLoading, error, login, clearError } = useAuth();

  // Retrieve origin route from location state if redirected by ProtectedRoute
  const destinationPath = (location.state as { from?: { pathname: string } })?.from?.pathname || '/simulator';

  useEffect(() => {
    // If user is already authenticated, redirect to requested destination
    if (isAuthenticated) {
      navigate(destinationPath, { replace: true });
    }
  }, [isAuthenticated, navigate, destinationPath]);

  // Clear previous auth errors when landing on login page
  useEffect(() => {
    clearError();
  }, [clearError]);

  const handleLoginExecution = async (credentials: LoginCredentials) => {
    const success = await login(credentials);
    if (success) {
      navigate(destinationPath, { replace: true });
    }
  };

  const scrollToLoginBox = () => {
    loginBoxRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen text-slate-800 relative selection:bg-cyan-500 selection:text-white">
      {/* ── Fixed Background Ambient Glows ─────────────────────────────────── */}
      <div className="fixed top-0 right-1/4 w-[500px] h-[500px] bg-cyan-500/15 rounded-full blur-[130px] pointer-events-none -z-10" />
      <div className="fixed bottom-1/4 left-10 w-[450px] h-[450px] bg-purple-600/15 rounded-full blur-[130px] pointer-events-none -z-10" />

      {/* ══════════════════════════════════════════════════════════════════════
          1. HERO SECTION (UPPER PAGE): Uploaded Image as Central Visual
          ══════════════════════════════════════════════════════════════════════ */}
      <HeroVisualSection onScrollToLogin={scrollToLoginBox} />

      {/* ══════════════════════════════════════════════════════════════════════
          2. LOGIN SECTION (LOWER PAGE): Reached After Scrolling
          ══════════════════════════════════════════════════════════════════════ */}
      <div
        id="login-box"
        ref={loginBoxRef}
        className="min-h-screen flex flex-col justify-center items-center py-16 px-4 relative z-10 border-t border-slate-800/80 bg-slate-950/60 backdrop-blur-xl"
      >
        <div className="max-w-md w-full space-y-6">
          {/* Header Tag */}
          <div className="text-center space-y-1.5">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-semibold mb-2 shadow-sm">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Secure Authentication Gateway</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              PayGuard AI Access Portal
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm max-w-sm mx-auto leading-relaxed">
              Authenticate to unlock the live multi-vector UPI fraud simulation & real-time telemetry console.
            </p>
          </div>

          {/* Frosted Login Card Container */}
          <div className="rounded-[32px] border border-white/50 bg-white/95 backdrop-blur-2xl shadow-[0_25px_80px_-15px_rgba(6,182,212,0.32)] p-7 sm:p-9 relative overflow-hidden transition-all">
            {/* Top Cyan Highlight Bar */}
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-cyan-400 via-indigo-500 to-purple-500" />

            {/* Brand Header */}
            <div className="text-center space-y-2 mb-6">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-400 via-blue-500 to-purple-600 shadow-lg shadow-cyan-500/30 ring-2 ring-white/60 mb-1">
                <ShieldCheck className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                  PAYGUARD AI
                </h1>
                <p className="text-[11px] font-bold text-indigo-600 uppercase tracking-wider font-mono mt-0.5">
                  INTELLIGENT UPI FRAUD DETECTION SYSTEM
                </p>
              </div>
            </div>

            {/* Identity Verification Subhead */}
            <div className="flex items-center justify-between border-b border-slate-200/80 pb-3 mb-5">
              <div className="flex items-center space-x-1.5 text-indigo-600 text-xs font-bold uppercase tracking-wider font-mono">
                <Lock className="w-3.5 h-3.5" />
                <span>Identity Verification</span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono px-2 py-0.5 rounded bg-slate-100 border border-slate-200">
                JWT Bearer v2.0
              </span>
            </div>

            {/* Login Form UI with 1-Click Demo Accounts */}
            <LoginForm
              onSubmit={handleLoginExecution}
              isLoading={isLoading}
              errorMessage={error}
            />
          </div>

          {/* Security & Disclaimer Footer */}
          <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 text-center space-y-1 backdrop-blur-md">
            <div className="flex items-center justify-center space-x-1.5 text-xs text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <span className="font-semibold text-slate-200">Protected Prototype Environment</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed font-mono">
              Passwords hashed with bcrypt (12 rounds) on FastAPI backend. Multi-vector ML risk evaluation.
            </p>
          </div>

          {/* Scroll Back To Top Button */}
          <div className="text-center pt-2">
            <button
              type="button"
              onClick={scrollToTop}
              className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-cyan-300 transition-colors font-mono"
            >
              <ArrowUp className="w-3.5 h-3.5" />
              <span>Back to Holographic Hero</span>
            </button>
          </div>
        </div>
      </div>

      {/* Atmospheric Ground Reflection */}
      <div className="h-14 w-full ambient-glow-reflection pointer-events-none shrink-0 flex items-center justify-center text-center text-[10px] text-cyan-300/40 font-mono">
        PAYGUARD AI • INTELLIGENT UPI FRAUD DETECTION SYSTEM • NAGARJUNA COLLEGE OF ENGINEERING AND TECHNOLOGY
      </div>
    </div>
  );
};
