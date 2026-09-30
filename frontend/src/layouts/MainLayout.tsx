/**
 * MainLayout.tsx - Production-style floating glass console inspired by modern cyber-fintech UI.
 * Features:
 * - Brand Name: PAYGUARD AI – INTELLIGENT UPI FRAUD DETECTION SYSTEM
 * - Deep royal purple/indigo sidebar with glowing electric blue active pill
 * - Pristine frosted-canvas workspace with soft ambient cyan glows and floor reflection
 * - Health indicator, user profile chip, and responsive navigation
 */

import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { 
  ShieldCheck, 
  LayoutDashboard, 
  Zap, 
  ReceiptText, 
  Bell, 
  Cpu, 
  CheckCircle2, 
  AlertTriangle, 
  BarChart3, 
  LogOut, 
  ChevronRight, 
  Menu, 
  X, 
  Sparkles 
} from 'lucide-react';
import { useHealth } from '../hooks/useHealth';
import { useAuth } from '../features/auth/hooks/useAuth';

export const MainLayout: React.FC = () => {
  const { health, loading, error } = useHealth();
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
    { to: '/simulator', label: 'ML Simulator', icon: Zap, end: false },
    { to: '/transactions', label: 'Transactions', icon: ReceiptText, end: false },
    { to: '/alerts', label: 'Fraud Alerts', icon: Bell, end: false },
    { to: '/analytics', label: 'Analytics', icon: BarChart3, end: false },
    { to: '/model', label: 'Model Version', icon: Cpu, end: false },
  ];

  return (
    <div className="min-h-screen text-slate-800 flex flex-col justify-between relative overflow-x-hidden selection:bg-cyan-500 selection:text-white">
      {/* Top Ambient Glow Highlights */}
      <div className="fixed top-0 right-1/4 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="fixed top-1/3 left-10 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Educational Notification Ribbon */}
      <div className="bg-slate-950/80 backdrop-blur-md border-b border-cyan-500/20 text-slate-300 py-1.5 px-4 text-xs z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2 truncate">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span className="truncate">
              <strong className="text-white font-semibold">PAYGUARD AI:</strong> Autonomous Multi-Vector UPI Fraud Risk Surveillance Engine
            </span>
          </div>
          <div className="hidden sm:flex items-center space-x-3 text-[11px] font-mono">
            {loading ? (
              <span className="text-slate-400 flex items-center">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping mr-1.5" />
                Connecting API...
              </span>
            ) : error ? (
              <span className="text-rose-400 flex items-center">
                <AlertTriangle className="w-3 h-3 mr-1" /> Backend Offline
              </span>
            ) : (
              <span className="text-emerald-400 flex items-center">
                <CheckCircle2 className="w-3 h-3 mr-1" /> {health?.database_backend || 'FastAPI Online'}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Main Floating Glass Tablet / Console */}
      <div className="flex-1 w-full max-w-[1440px] mx-auto p-2 sm:p-5 lg:p-7 flex flex-col justify-center">
        <div className="rounded-[28px] lg:rounded-[34px] border border-white/30 bg-slate-900/40 backdrop-blur-2xl shadow-[0_25px_80px_-15px_rgba(6,182,212,0.28)] overflow-hidden flex flex-col lg:flex-row min-h-[820px] transition-all">
          
          {/* ══════════════════════════════════════════════════════════════════
              LEFT SIDEBAR: Deep Purple-Indigo Gradient (Matching Reference Image)
             ══════════════════════════════════════════════════════════════════ */}
          <aside className="w-full lg:w-64 bg-gradient-to-b from-[#211342] via-[#291750] to-[#180e30] p-5 lg:p-6 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-indigo-500/20 shrink-0">
            {/* Logo & Header */}
            <div>
              <div className="flex items-center justify-between pb-6 border-b border-indigo-500/20">
                <div className="flex items-center space-x-3">
                  {/* Glowing Wireframe Hexagon Icon */}
                  <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-400 via-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/30 ring-2 ring-white/30">
                    <ShieldCheck className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h1 className="text-base font-extrabold text-white tracking-wide leading-tight">
                      PayGuard AI
                    </h1>
                    <span className="text-[10px] uppercase font-mono tracking-widest text-cyan-300/80 font-bold block">
                      UPI Detection
                    </span>
                  </div>
                </div>

                {/* Mobile Menu Toggle Button */}
                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="lg:hidden p-2 text-indigo-300 hover:text-white"
                >
                  {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </button>
              </div>

              {/* Navigation Items */}
              <nav className={`mt-6 space-y-1.5 ${mobileMenuOpen ? 'block' : 'hidden lg:block'}`}>
                {navLinks.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.end}
                      onClick={() => setMobileMenuOpen(false)}
                      className={({ isActive }) =>
                        `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                          isActive
                            ? 'bg-gradient-to-r from-[#4f46e5] via-[#3b82f6] to-[#0ea5e9] text-white shadow-[0_6px_20px_rgba(14,165,233,0.4)] translate-x-1'
                            : 'text-indigo-200/70 hover:text-white hover:bg-white/5'
                        }`
                      }
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className="w-4 h-4 shrink-0" />
                        <span>{item.label}</span>
                      </div>
                      <ChevronRight className="w-3.5 h-3.5 opacity-60" />
                    </NavLink>
                  );
                })}
              </nav>
            </div>

            {/* Bottom Sidebar Status / Engine Tag */}
            <div className="pt-6 mt-6 border-t border-indigo-500/20 hidden lg:block">
              <div className="p-3 rounded-2xl bg-indigo-950/40 border border-indigo-500/20 text-indigo-200/90 text-[11px] space-y-1.5">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                  <span className="font-bold text-white uppercase tracking-wider text-[10px]">
                    XGBoost Champion
                  </span>
                </div>
                <p className="text-[10px] text-indigo-300/70 leading-relaxed font-mono">
                  Multi-Vector Risk Engine Active • Latency &lt;45ms
                </p>
              </div>
            </div>
          </aside>

          {/* ══════════════════════════════════════════════════════════════════
              MAIN CONTENT CANVAS: Frosted Ice-Glass (Matching Reference Image)
             ══════════════════════════════════════════════════════════════════ */}
          <div className="flex-1 flex flex-col frost-canvas relative overflow-hidden">
            {/* Top Workspace Header */}
            <header className="px-6 py-4.5 border-b border-slate-200/80 bg-white/70 backdrop-blur-md flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sticky top-0 z-40">
              {/* Official Project Title Heading */}
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                    PAYGUARD AI
                  </span>
                  <span className="text-slate-400 font-light text-xl">|</span>
                  <span className="text-xs sm:text-sm font-bold text-indigo-600 tracking-wide uppercase font-mono">
                    INTELLIGENT UPI FRAUD DETECTION SYSTEM
                  </span>
                </div>
                <p className="text-slate-500 text-xs mt-0.5 hidden md:block">
                  Academic Prototype • Nagarjuna College of Engineering and Technology
                </p>
              </div>

              {/* Right Side: User Profile Chip matching reference image [ | Dan hookua > ] */}
              <div className="flex items-center space-x-3 self-end sm:self-auto">
                {isAuthenticated && user ? (
                  <div className="flex items-center space-x-2">
                    <div className="px-3.5 py-1.5 rounded-full bg-white shadow-sm border border-slate-200 flex items-center space-x-2 text-xs text-slate-700 hover:border-indigo-300 transition-colors">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-cyan-500 to-indigo-500 flex items-center justify-center text-white text-[10px] font-bold">
                        {user.name.charAt(0)}
                      </div>
                      <span className="font-semibold text-slate-800">{user.name}</span>
                      <span className="text-[10px] uppercase font-mono text-indigo-600 font-bold px-1.5 py-0.2 rounded bg-indigo-50">
                        {user.role}
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={logout}
                      className="p-2 rounded-full bg-white hover:bg-rose-50 text-slate-500 hover:text-rose-600 border border-slate-200 transition-colors shadow-sm"
                      title="Sign Out"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ) : (
                  <NavLink
                    to="/login"
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 text-white text-xs font-bold shadow-md shadow-indigo-500/25 hover:opacity-95 transition-opacity"
                  >
                    Analyst Login
                  </NavLink>
                )}
              </div>
            </header>

            {/* Child Page Outlet with Frosted Canvas Area */}
            <main className="flex-1 p-5 sm:p-7 lg:p-8 overflow-y-auto">
              <Outlet />
            </main>
          </div>
        </div>
      </div>

      {/* Atmospheric Ground Reflection (as depicted in 3D floating reference photo) */}
      <div className="h-16 w-full ambient-glow-reflection pointer-events-none mt-2 shrink-0 flex items-center justify-center text-center text-[11px] text-cyan-300/40 font-mono">
        PAYGUARD AI • INTELLIGENT UPI FRAUD DETECTION SYSTEM • FASTAPI • SCIKIT-LEARN • XGBOOST • REACT
      </div>
    </div>
  );
};
