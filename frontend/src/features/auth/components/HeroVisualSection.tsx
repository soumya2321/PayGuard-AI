/**
 * HeroVisualSection.tsx - Premium animated holographic fintech hero section.
 * Features:
 * - Central visual: Uploaded smartphone financial projection image
 * - Dynamic IN-IMAGE MOVING HOLOGRAPHIC ELEMENTS:
 *   1. Left Floating Holographic $ Tile (drifting, rotating, pulsing)
 *   2. Central Floating Holographic Money Bag (breathing, scaling, lifting, particle aura)
 *   3. Right Floating Holographic $ Tile (floating out-of-phase with glowing neon edges)
 *   4. Floating Holographic Banknote (hovering, swaying, cyan shimmer)
 *   5. Glowing Zigzag Growth Arrow with electric pulse traveling to the tip
 *   6. Dynamic 3D Equalizer Bars cluster rising and dancing on the phone screen
 *   7. Radiating holographic currency micro-particles ($ and ✦) rising from phone
 *   8. Interactive click burst on Money Bag and $ tiles (+₹50,000 Verified!)
 *   9. Surrounding glassmorphism stat cards (+₹24,580, Payment Successful ₹12,500, Risk Score 2.4%)
 *   10. Mouse 3D perspective parallax & smooth scroll trigger to login box
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import {
  ShieldCheck,
  TrendingUp,
  Zap,
  Sparkles,
  Lock,
  ChevronDown,
  ArrowRight,
  Activity
} from 'lucide-react';
import heroPhoneImg from '../../../assets/hero-phone.png';

// Number count-up hook for realistic rolling digits
function useCountUp(endValue: number, durationMs: number = 2200, startTrigger: boolean = true) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (!startTrigger) return;
    let startTime: number | null = null;
    let animationFrameId: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / durationMs, 1);
      // Ease out cubic
      const easeOut = 1 - Math.pow(1 - progress, 3);
      setValue(Math.floor(easeOut * endValue));

      if (progress < 1) {
        animationFrameId = requestAnimationFrame(animate);
      } else {
        setValue(endValue);
      }
    };

    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, [endValue, durationMs, startTrigger]);

  return value;
}

export const HeroVisualSection: React.FC<{ onScrollToLogin: () => void }> = ({ onScrollToLogin }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(containerRef, { once: true, margin: '-50px' });

  // Mouse Parallax Coordinates (-0.5 to 0.5)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  // Interactive Click State for Money Bag and Tiles
  const [bagClicked, setBagClicked] = useState(false);
  const [leftTileRotated, setLeftTileRotated] = useState(0);
  const [rightTileRotated, setRightTileRotated] = useState(0);
  const [burstToast, setBurstToast] = useState<string | null>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    setMousePos({ x, y });
  };

  const handleMouseLeave = () => {
    setMousePos({ x: 0, y: 0 });
    setIsHovered(false);
  };

  const triggerMoneyBagBurst = () => {
    setBagClicked(true);
    setBurstToast('+₹50,000 Holographic UPI Transfer Verified!');
    setTimeout(() => setBagClicked(false), 800);
    setTimeout(() => setBurstToast(null), 3000);
  };

  const triggerLeftTileSpin = () => {
    setLeftTileRotated((prev) => prev + 360);
    setBurstToast('Dollar Token Authenticated: $2,500');
    setTimeout(() => setBurstToast(null), 2500);
  };

  const triggerRightTileSpin = () => {
    setRightTileRotated((prev) => prev - 360);
    setBurstToast('Digital Treasury Asset Verified: $4,800');
    setTimeout(() => setBurstToast(null), 2500);
  };

  // Counting values for stat cards
  const revenueCount = useCountUp(24580, 2400, isInView);
  const txAmountCount = useCountUp(12500, 2000, isInView);
  const receivedAmountCount = useCountUp(8500, 2200, isInView);
  const [percentValue, setPercentValue] = useState('0.0');

  useEffect(() => {
    if (!isInView) return;
    const steps = ['0.0', '4.2', '8.7', '12.4', '15.8', '18.6'];
    let idx = 0;
    const interval = setInterval(() => {
      idx++;
      if (idx < steps.length) {
        setPercentValue(steps[idx]);
      } else {
        clearInterval(interval);
      }
    }, 380);
    return () => clearInterval(interval);
  }, [isInView]);

  return (
    <section
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="relative min-h-[95vh] flex flex-col justify-between items-center px-4 pt-4 pb-8 overflow-hidden select-none"
    >
      {/* ── Background Cyber Ambient Glows ─────────────────────────────────── */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[550px] bg-gradient-to-tr from-cyan-500/20 via-blue-600/15 to-purple-600/25 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-purple-600/15 rounded-full blur-[100px] pointer-events-none -z-10" />

      {/* Floating Ambient Particles */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden -z-5">
        {[...Array(16)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full"
            style={{
              width: i % 2 === 0 ? '4px' : '6px',
              height: i % 2 === 0 ? '4px' : '6px',
              backgroundColor: i % 3 === 0 ? '#38bdf8' : i % 3 === 1 ? '#a855f7' : '#22d3ee',
              boxShadow: '0 0 10px rgba(56, 189, 248, 0.9)',
              left: `${8 + (i * 5.8)}%`,
              top: `${15 + (i * 4.9)}%`,
            }}
            animate={{
              y: [-10, -70, -10],
              x: [0, (i % 2 === 0 ? 18 : -18), 0],
              opacity: [0.2, 0.9, 0.2],
              scale: [0.8, 1.4, 0.8],
            }}
            transition={{
              duration: 4.5 + (i % 4),
              repeat: Infinity,
              ease: 'easeInOut',
              delay: i * 0.3,
            }}
          />
        ))}
      </div>

      {/* ── Top Hero Header Ribbon ─────────────────────────────────────────── */}
      <div className="text-center max-w-3xl mx-auto z-10 pt-2 sm:pt-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-slate-900/80 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-semibold mb-3 shadow-[0_0_20px_rgba(6,182,212,0.25)] backdrop-blur-md"
        >
          <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span>PAYGUARD AI • INTELLIGENT UPI FRAUD DETECTION SYSTEM</span>
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.85, delay: 0.15 }}
          className="text-3xl sm:text-5xl md:text-6xl font-black text-white tracking-tight leading-tight"
        >
          Next-Gen Autonomous <br />
          <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-purple-400 bg-clip-text text-transparent drop-shadow-[0_0_25px_rgba(34,211,238,0.4)]">
            Live Holographic Money Engine
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.85, delay: 0.3 }}
          className="text-slate-400 text-xs sm:text-sm md:text-base mt-2.5 max-w-xl mx-auto leading-relaxed"
        >
          Watch the floating currency holograms, animated rising graph, and real-time telemetry stream dynamically from the smartphone.
        </motion.p>
      </div>

      {/* Interactive Toast Notification when Money Bag or Tiles are Clicked */}
      <AnimatePresence>
        {burstToast && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.85 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.85 }}
            className="fixed top-24 z-50 px-5 py-2.5 rounded-2xl bg-slate-900/90 border border-cyan-400 text-cyan-300 text-xs font-mono font-bold shadow-[0_0_30px_rgba(6,182,212,0.6)] backdrop-blur-xl flex items-center space-x-2"
          >
            <Sparkles className="w-4 h-4 text-cyan-400 animate-spin" />
            <span>{burstToast}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Main Center Stage: Phone Visual & Holographic Layers ────────────── */}
      <div 
        className="relative w-full max-w-4xl my-auto flex items-center justify-center py-4"
        style={{ perspective: 1200 }}
      >
        {/* Holographic Conic Projection Beam from Phone Base */}
        <div className="absolute w-[460px] h-[420px] -top-12 bg-gradient-to-t from-cyan-400/25 via-blue-500/10 to-transparent blur-2xl pointer-events-none rounded-t-full transform -rotate-6" />

        {/* ── CENTRAL PHONE IMAGE CONTAINER (WITH IN-IMAGE MOVING ICONS) ─────── */}
        <motion.div
          initial={{ opacity: 0, scale: 0.92, filter: 'blur(10px)' }}
          animate={{ 
            opacity: 1, 
            scale: 1, 
            filter: 'blur(0px)',
          }}
          transition={{ duration: 1.6, ease: [0.16, 1, 0.3, 1] }}
          style={{
            transformStyle: 'preserve-3d',
            rotateX: mousePos.y * -14,
            rotateY: mousePos.x * 16,
          }}
          onHoverStart={() => setIsHovered(true)}
          onHoverEnd={() => setIsHovered(false)}
          className="relative group rounded-3xl p-1 bg-gradient-to-b from-cyan-500/30 via-purple-500/20 to-slate-900/60 shadow-[0_25px_90px_-15px_rgba(6,182,212,0.35)] transition-shadow duration-500"
        >
          {/* Subtle Outer Neon Border Glow */}
          <div className={`absolute -inset-1 rounded-3xl bg-gradient-to-r from-cyan-500 via-sky-400 to-purple-600 blur-md transition-opacity duration-500 -z-10 ${
            isHovered ? 'opacity-70' : 'opacity-35'
          }`} />

          {/* Floating Phone Frame */}
          <motion.div
            animate={{
              y: [0, -10, 0],
            }}
            transition={{
              duration: 3.8,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            className="relative rounded-2xl overflow-hidden bg-slate-950/70"
          >
            {/* The Authentic Uploaded Image (Visually Unchanged Backdrop) */}
            <img
              src={heroPhoneImg}
              alt="PayGuard AI Holographic Smartphone UPI Telemetry"
              className="w-auto h-[380px] sm:h-[450px] md:h-[500px] object-contain rounded-2xl transition-transform duration-700 select-none pointer-events-none"
            />

            {/* Subtle Holographic Scanline Overlay on Image */}
            <div className="absolute inset-0 holo-scanline pointer-events-none opacity-30 mix-blend-overlay" />

            {/* ══════════════════════════════════════════════════════════════════
                DIRECT IN-IMAGE DYNAMIC MOVING HOLOGRAPHIC OVERLAYS
                ══════════════════════════════════════════════════════════════════ */}

            {/* 1. LEFT MOVING HOLOGRAPHIC $ TILE */}
            <motion.div
              onClick={triggerLeftTileSpin}
              title="Click to spin holographic Dollar Tile"
              animate={{
                y: [-7, 9, -7],
                rotate: [-4 + leftTileRotated, 5 + leftTileRotated, -4 + leftTileRotated],
                scale: [0.98, 1.05, 0.98],
              }}
              transition={{
                duration: 3.6,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
              style={{
                left: '27.4%',
                top: '25.0%',
                width: '13.2%',
                height: '13.2%',
              }}
              className="absolute z-20 cursor-pointer group/tile flex items-center justify-center"
            >
              {/* Animated Glowing Tile Body */}
              <div className="w-full h-full rounded-xl bg-cyan-950/70 border-2 border-cyan-300 shadow-[0_0_16px_rgba(34,211,238,0.95)] backdrop-blur-md relative flex items-center justify-center transition-all duration-300 group-hover/tile:scale-110 group-hover/tile:border-white">
                {/* Top Clip Tab matching image */}
                <div className="absolute -top-2.5 left-1/2 -translate-x-1/2 w-4 h-2.5 rounded-t-sm bg-cyan-400/90 border border-cyan-200" />
                {/* Centered Glowing $ */}
                <span className="text-white text-base sm:text-lg md:text-xl font-black font-mono drop-shadow-[0_0_8px_#ffffff]">
                  $
                </span>
                {/* Pulsing Corner Beacon */}
                <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-cyan-300 animate-ping" />
              </div>
            </motion.div>

            {/* 2. CENTRAL MOVING HOLOGRAPHIC MONEY BAG */}
            <motion.div
              onClick={triggerMoneyBagBurst}
              title="Click to trigger Money Bag burst animation!"
              animate={{
                y: [-12, 6, -12],
                scale: bagClicked ? [1, 1.25, 1] : [1, 1.07, 1],
                rotate: [-2, 2, -2],
              }}
              transition={{
                duration: 4.2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
              style={{
                left: '43.0%',
                top: '29.5%',
                width: '15.5%',
                height: '17.8%',
              }}
              className="absolute z-25 cursor-pointer group/bag flex items-center justify-center"
            >
              {/* Dynamic Glowing SVG Money Bag */}
              <div className="relative w-full h-full flex items-center justify-center transition-transform duration-300 group-hover/bag:scale-110">
                <svg
                  viewBox="0 0 100 120"
                  className="w-full h-full filter drop-shadow-[0_0_18px_rgba(34,211,238,1)] overflow-visible"
                >
                  <defs>
                    <linearGradient id="moneyBagGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
                      <stop offset="35%" stopColor="#67e8f9" stopOpacity="0.85" />
                      <stop offset="100%" stopColor="#0891b2" stopOpacity="0.9" />
                    </linearGradient>
                    <filter id="cyanNeon" x="-20%" y="-20%" width="140%" height="140%">
                      <feGaussianBlur stdDeviation="3" result="blur" />
                      <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                  </defs>

                  {/* Tied Ruffled Frill at Top */}
                  <path
                    d="M 32,15 C 38,8 48,6 52,14 C 58,6 68,9 70,16 C 65,22 35,22 32,15 Z"
                    fill="url(#moneyBagGrad)"
                    stroke="#ffffff"
                    strokeWidth="2"
                  />

                  {/* Tie Ribbon Band */}
                  <rect x="36" y="21" width="30" height="6" rx="3" fill="#22d3ee" stroke="#ffffff" strokeWidth="1.5" />

                  {/* Rounded Pouch Body */}
                  <path
                    d="M 38,27 C 15,35 10,75 16,98 C 22,112 80,112 86,98 C 92,75 87,35 64,27 Z"
                    fill="url(#moneyBagGrad)"
                    stroke="#ffffff"
                    strokeWidth="2.5"
                    filter="url(#cyanNeon)"
                  />

                  {/* Prominent Dollar Symbol in Center */}
                  <text
                    x="51"
                    y="76"
                    textAnchor="middle"
                    fill="#083344"
                    fontSize="36"
                    fontWeight="900"
                    fontFamily="monospace"
                  >
                    $
                  </text>
                </svg>

                {/* Sparkling Orbiting Particles Around Money Bag */}
                <motion.div
                  animate={{
                    rotate: [0, 360],
                  }}
                  transition={{
                    duration: 6,
                    repeat: Infinity,
                    ease: 'linear',
                  }}
                  className="absolute inset-0 pointer-events-none"
                >
                  <span className="absolute -top-2 left-1/4 w-2 h-2 rounded-full bg-white shadow-[0_0_8px_#ffffff]" />
                  <span className="absolute -bottom-1 right-1/4 w-1.5 h-1.5 rounded-full bg-cyan-300 shadow-[0_0_8px_#22d3ee]" />
                </motion.div>
              </div>
            </motion.div>

            {/* 3. RIGHT MOVING HOLOGRAPHIC $ TILE */}
            <motion.div
              onClick={triggerRightTileSpin}
              title="Click to spin right holographic Dollar Tile"
              animate={{
                y: [7, -10, 7],
                rotate: [4 + rightTileRotated, -5 + rightTileRotated, 4 + rightTileRotated],
                scale: [1.03, 0.97, 1.03],
              }}
              transition={{
                duration: 3.9,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: 0.25,
              }}
              style={{
                left: '60.8%',
                top: '23.0%',
                width: '14.0%',
                height: '14.0%',
              }}
              className="absolute z-20 cursor-pointer group/tile flex items-center justify-center"
            >
              {/* Animated Glowing Right Tile Body */}
              <div className="w-full h-full rounded-xl bg-cyan-950/70 border-2 border-cyan-300 shadow-[0_0_16px_rgba(34,211,238,0.95)] backdrop-blur-md relative flex items-center justify-center transition-all duration-300 group-hover/tile:scale-110 group-hover/tile:border-white">
                {/* Top Clip Tab */}
                <div className="absolute -top-2.5 left-1/2 -translate-x-1/2 w-4 h-2.5 rounded-t-sm bg-cyan-400/90 border border-cyan-200" />
                {/* Centered Glowing $ */}
                <span className="text-white text-base sm:text-lg md:text-xl font-black font-mono drop-shadow-[0_0_8px_#ffffff]">
                  $
                </span>
                <span className="absolute bottom-1 left-1 w-1.5 h-1.5 rounded-full bg-cyan-300 animate-ping" />
              </div>
            </motion.div>

            {/* 4. MOVING HOLOGRAPHIC BANKNOTE (LOWER-LEFT) */}
            <motion.div
              animate={{
                y: [-5, 6, -5],
                rotate: [-3, 3, -3],
                x: [-3, 3, -3],
              }}
              transition={{
                duration: 4.0,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: 0.5,
              }}
              style={{
                left: '27.0%',
                top: '42.8%',
                width: '15.5%',
                height: '8.8%',
              }}
              className="absolute z-20 flex items-center justify-center pointer-events-auto cursor-pointer"
            >
              <div className="w-full h-full rounded-lg bg-cyan-950/80 border-2 border-cyan-300 shadow-[0_0_14px_rgba(34,211,238,0.9)] flex items-center justify-between px-1.5 backdrop-blur-sm hover:scale-105 transition-transform">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-300" />
                <div className="w-6 h-4 rounded-full border border-cyan-300 flex items-center justify-center">
                  <span className="text-white text-[11px] font-bold font-mono">$</span>
                </div>
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-300" />
              </div>
            </motion.div>

            {/* 5. ANIMATED PULSING RISING GRAPH ARROW */}
            <div
              style={{
                left: '28.0%',
                top: '38.5%',
                width: '46.5%',
                height: '21.5%',
              }}
              className="absolute z-15 pointer-events-none"
            >
              <svg viewBox="0 0 200 90" className="w-full h-full overflow-visible">
                <defs>
                  <linearGradient id="arrowBeamGrad" x1="0%" y1="100%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.4" />
                    <stop offset="70%" stopColor="#38bdf8" stopOpacity="0.9" />
                    <stop offset="100%" stopColor="#ffffff" stopOpacity="1" />
                  </linearGradient>
                </defs>

                {/* Animated Electric Traveling Pulse Stroke */}
                <motion.path
                  d="M 5,80 L 40,65 L 75,75 L 115,48 L 145,55 L 185,15"
                  fill="none"
                  stroke="url(#arrowBeamGrad)"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: [0, 1, 1, 0] }}
                  transition={{
                    duration: 3.5,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                  className="filter drop-shadow-[0_0_10px_#22d3ee]"
                />

                {/* Glowing Pulsing Arrow Tip */}
                <motion.polygon
                  points="185,8 200,14 188,25"
                  fill="#ffffff"
                  stroke="#38bdf8"
                  strokeWidth="2"
                  animate={{
                    scale: [1, 1.3, 1],
                    filter: [
                      'drop-shadow(0 0 6px #ffffff)',
                      'drop-shadow(0 0 16px #38bdf8)',
                      'drop-shadow(0 0 6px #ffffff)',
                    ],
                  }}
                  transition={{
                    duration: 2.0,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />
              </svg>
            </div>

            {/* 6. DYNAMIC LIVE 3D EQUALIZER BARS CLUSTER */}
            <div
              style={{
                left: '42.0%',
                top: '49.0%',
                width: '31.0%',
                height: '13.5%',
              }}
              className="absolute z-15 flex items-end justify-between px-1 pointer-events-none"
            >
              {[15, 35, 22, 55, 40, 75, 60, 90, 70, 85, 48, 65, 30].map((baseH, idx) => (
                <motion.div
                  key={idx}
                  className="w-1 rounded-t-sm bg-gradient-to-t from-cyan-500/40 via-cyan-400 to-white shadow-[0_0_8px_rgba(34,211,238,0.8)]"
                  animate={{
                    height: [`${baseH * 0.4}%`, `${baseH}%`, `${baseH * 0.6}%`],
                  }}
                  transition={{
                    duration: 1.2 + ((idx % 4) * 0.3),
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: idx * 0.1,
                  }}
                />
              ))}
            </div>

            {/* 7. LIVE FLOATING CURRENCY PARTICLES RISING FROM PHONE SCREEN */}
            <div className="absolute inset-0 pointer-events-none z-30">
              {[
                { sym: '$', left: '35%', delay: 0 },
                { sym: '₹', left: '48%', delay: 1.2 },
                { sym: '$', left: '55%', delay: 2.0 },
                { sym: '✦', left: '65%', delay: 0.7 },
                { sym: '$', left: '42%', delay: 2.7 },
              ].map((p, idx) => (
                <motion.div
                  key={idx}
                  style={{ left: p.left, bottom: '40%' }}
                  animate={{
                    y: [0, -110],
                    opacity: [0, 0.9, 0],
                    scale: [0.7, 1.2, 0.6],
                  }}
                  transition={{
                    duration: 3.2,
                    repeat: Infinity,
                    ease: 'easeOut',
                    delay: p.delay,
                  }}
                  className="absolute text-cyan-300 font-mono font-black text-xs drop-shadow-[0_0_8px_#22d3ee]"
                >
                  {p.sym}
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>

        {/* ════════════════════════════════════════════════════════════════════
            SURROUNDING HOLOGRAPHIC FINTECH STAT CARDS
            ════════════════════════════════════════════════════════════════════ */}

        {/* Floating Telemetry Graph Card (Bottom Right) */}
        <motion.div
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.2, delay: 0.9 }}
          style={{
            x: mousePos.x * 12,
            y: mousePos.y * 10,
          }}
          className="absolute -bottom-4 right-1/2 translate-x-1/2 sm:translate-x-0 sm:right-4 sm:bottom-8 z-30 pointer-events-none"
        >
          <div className="relative p-3 sm:p-4 rounded-2xl holo-glass-card shadow-2xl backdrop-blur-xl border border-cyan-400/30 w-56 sm:w-64">
            <div className="flex items-center justify-between text-xs pb-2 border-b border-cyan-500/20">
              <span className="flex items-center space-x-1.5 text-cyan-300 font-mono font-semibold text-[11px]">
                <Activity className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                <span>TELEMETRY STREAM</span>
              </span>
              <span className="text-[10px] text-emerald-400 font-mono font-bold bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/30">
                LIVE
              </span>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div>
                <span className="text-[10px] text-slate-400 block font-mono">Current Risk Score</span>
                <span className="text-lg font-black text-white font-mono">0.024 (Low)</span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-400 block font-mono">Decision Latency</span>
                <span className="text-xs font-bold text-cyan-300 font-mono">38 ms</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Top-Right Floating Stat Card: +₹24,580 & +18.6% */}
        <motion.div
          initial={{ opacity: 0, y: -30, scale: 0.75, rotate: -3 }}
          animate={{ opacity: 1, y: 0, scale: 1, rotate: 0 }}
          transition={{ duration: 1.1, delay: 0.7, type: 'spring', bounce: 0.35 }}
          style={{
            x: mousePos.x * -26,
            y: mousePos.y * -20,
          }}
          className="absolute -top-4 sm:top-2 right-0 sm:-right-6 z-30"
        >
          <motion.div
            animate={{
              y: [0, -8, 0],
            }}
            transition={{
              duration: 4.8,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.6,
            }}
            className="p-4 sm:p-5 rounded-2xl holo-glass-card shadow-2xl backdrop-blur-xl border border-cyan-400/40 relative overflow-hidden w-52 sm:w-60 hover:border-cyan-300 transition-colors"
          >
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-400/10 rounded-full blur-xl pointer-events-none" />
            <div className="flex items-center justify-between text-xs text-cyan-300 font-mono font-semibold mb-1">
              <span>REVENUE GROWTH</span>
              <div className="flex items-center text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/25">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>+{percentValue}%</span>
              </div>
            </div>

            <div className="text-2xl sm:text-3xl font-black text-white tracking-tight font-mono mt-1 drop-shadow-[0_0_12px_rgba(255,255,255,0.3)]">
              +₹{revenueCount.toLocaleString('en-IN')}
            </div>

            <p className="text-[10px] text-slate-400 mt-1 flex items-center space-x-1 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>Verified UPI Transfers Today</span>
            </p>
          </motion.div>
        </motion.div>

        {/* Left Floating Card: ✓ Payment Successful ₹12,500 */}
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.75, rotate: 3 }}
          animate={{ opacity: 1, y: 0, scale: 1, rotate: 0 }}
          transition={{ duration: 1.1, delay: 1.0, type: 'spring', bounce: 0.35 }}
          style={{
            x: mousePos.x * 28,
            y: mousePos.y * 22,
          }}
          className="absolute -bottom-6 sm:bottom-6 left-0 sm:-left-8 z-30"
        >
          <motion.div
            animate={{
              y: [0, -10, 0],
            }}
            transition={{
              duration: 5.2,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1.0,
            }}
            className="p-3.5 sm:p-4 rounded-2xl holo-glass-card shadow-2xl backdrop-blur-xl border border-emerald-500/40 w-52 sm:w-64 hover:border-emerald-400 transition-colors"
          >
            <div className="flex items-center space-x-3">
              {/* Animated Self-Drawing Checkmark */}
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-400/50 flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(16,185,129,0.4)]">
                <svg className="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <motion.path
                    d="M5 13l4 4L19 7"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 1.2, delay: 1.3, ease: 'easeOut' }}
                  />
                </svg>
              </div>

              <div>
                <span className="text-[11px] font-bold text-emerald-400 flex items-center">
                  Payment Successful
                </span>
                <p className="text-base sm:text-lg font-black text-white font-mono">
                  ₹{txAmountCount.toLocaleString('en-IN')}
                </p>
              </div>
            </div>

            <div className="mt-2 pt-2 border-t border-slate-800 text-[10px] text-slate-400 flex items-center justify-between font-mono">
              <span>HDFC → SBI Instant</span>
              <span className="text-emerald-400">0.03s Settle</span>
            </div>
          </motion.div>
        </motion.div>

        {/* Top-Left Floating Holographic Card: ⚡ AI Fraud Detection (Risk Score 2.4%) */}
        <motion.div
          initial={{ opacity: 0, y: -25, scale: 0.8 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 1.0, delay: 1.25, type: 'spring', bounce: 0.3 }}
          style={{
            x: mousePos.x * 20,
            y: mousePos.y * -16,
          }}
          className="absolute top-10 sm:top-8 left-4 sm:left-12 z-25 hidden sm:block"
        >
          <motion.div
            animate={{
              y: [0, -7, 0],
            }}
            transition={{
              duration: 4.4,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.8,
            }}
            className="p-3 sm:p-3.5 rounded-2xl holo-glass-card shadow-xl backdrop-blur-xl border border-cyan-400/40 w-48 hover:border-cyan-300 transition-colors"
          >
            <div className="flex items-center space-x-2 text-xs font-bold text-cyan-300">
              <Zap className="w-4 h-4 text-cyan-400 animate-pulse" />
              <span>AI Fraud Detection</span>
            </div>
            <div className="mt-1 flex items-baseline space-x-1.5">
              <span className="text-lg font-black text-emerald-400 font-mono">2.4%</span>
              <span className="text-[10px] text-slate-400 font-mono">Risk Score</span>
            </div>
            <div className="mt-1.5 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-full w-[12%]" />
            </div>
          </motion.div>
        </motion.div>

        {/* Holographic Notification: Payment Received +₹8,500 */}
        <motion.div
          initial={{ opacity: 0, y: 25, scale: 0.7 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.95, delay: 1.45, type: 'spring', bounce: 0.3 }}
          style={{
            x: mousePos.x * -18,
            y: mousePos.y * 14,
          }}
          className="absolute -bottom-8 sm:bottom-0 right-4 sm:right-28 z-25 hidden md:block"
        >
          <motion.div
            animate={{
              y: [0, -9, 0],
            }}
            transition={{
              duration: 4.9,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1.2,
            }}
            className="p-3 rounded-2xl holo-glass-card backdrop-blur-xl border border-sky-400/30 flex items-center space-x-2.5 shadow-xl"
          >
            <div className="w-8 h-8 rounded-xl bg-sky-500/20 border border-sky-400/40 flex items-center justify-center text-sky-300">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 block font-mono">Payment Received</span>
              <span className="text-xs font-bold text-sky-300 font-mono">
                +₹{receivedAmountCount.toLocaleString('en-IN')}
              </span>
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* ── Bottom Section: Scroll-To-Login Prompt Button ──────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, delay: 1.6 }}
        className="z-20 text-center mt-3 flex flex-col items-center"
      >
        <button
          type="button"
          onClick={onScrollToLogin}
          className="group px-6 py-3 rounded-full bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:opacity-95 text-white font-bold text-xs shadow-[0_10px_35px_rgba(6,182,212,0.4)] flex items-center space-x-2.5 transition-all transform hover:scale-105 active:scale-95"
        >
          <Lock className="w-4 h-4 text-cyan-200" />
          <span>ACCESS SECURE ANALYST TERMINAL</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>

        <button
          type="button"
          onClick={onScrollToLogin}
          className="mt-3 flex items-center space-x-1.5 text-xs text-slate-400 hover:text-cyan-300 transition-colors animate-bounce"
        >
          <span>Scroll down to sign in</span>
          <ChevronDown className="w-4 h-4" />
        </button>
      </motion.div>
    </section>
  );
};
