/**
 * SimulatorPage.tsx - Production-style Real-Time UPI Transaction Fraud Simulator.
 * Features:
 * - Real-time GPS Location Detector (HTML5 Geolocation API + reverse lookup)
 * - Hardware / Device Fingerprint Detector (navigator.userAgent)
 * - Time-of-Day Anomaly Controller (e.g., 03:15 AM off-peak window)
 * - 1-Click "Problem Statement Scenario" Preset (₹45,000 + New Device + Kolkata + 03:15 AM)
 * - Behavioral & Geographic Baseline Comparison Banners
 * - Multi-Vector Risk Engine Evaluation with Explainable AI Breakdown
 * - Styled to match the cyber-pastel frosted glass design from the reference image
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Zap, 
  RotateCcw, 
  ArrowRight, 
  CheckCircle, 
  ShieldAlert, 
  Smartphone, 
  MapPin, 
  Clock, 
  AlertTriangle, 
  Navigation, 
  Radio, 
  ShieldCheck, 
  Sparkles, 
  KeyRound, 
  ExternalLink, 
  CheckCircle2, 
  XCircle, 
  Lock 
} from 'lucide-react';
import { apiService } from '../services/api';
import type { 
  TransactionFeatureInput, 
  TransactionRecord 
} from '../types';
import { RiskMeter } from '../components/RiskMeter';
import { RiskFactorsList } from '../components/RiskFactorsList';
import { RiskBadge } from '../components/RiskBadge';
import { formatCurrency } from '../utils/formatters';
import { ErrorAlert } from '../components/ErrorAlert';

// Default baseline telemetry (normalized scale)
const defaultFeatures: TransactionFeatureInput = {
  amount: 0.0,
  session_duration: 0.0,
  receiver_transaction_history: 0.5,
  transaction_amount_vs_sender_history: 0.0,
  geographic_disparity: 0.0,
  transaction_time_of_day: 0.0,
  time_between_link_click_and_transaction: 0.0,
  input_timing_consistency: 0.5,
  keyboard_input_speed: 0.0,
  input_pause_patterns: 0.0,
  screen_active_time: 0.0,
  geographic_location_vs_ip: 0.0,
  background_data_usage: 0.0,
  pin_entry_speed: 0.0,
  request_amount_roundness: 0.0,
  request_acceptance_rate: 0.0,
  time_to_respond_to_request: 0.0,
  user_id_freq: 0.0,
};

// Test Scenarios with Problem Statement as Hero Preset
interface PresetScenario {
  id: string;
  name: string;
  badge: string;
  badgeColor: string;
  description: string;
  sender_upi_id: string;
  receiver_upi_id: string;
  amount_inr: number;
  location: string;
  device_type: string;
  time_of_day: string;
  features: Partial<TransactionFeatureInput>;
}

const PRESET_SCENARIOS: PresetScenario[] = [
  {
    id: 'problem_statement_case',
    name: '🎯 Suspicious Account Takeover: ₹45,000 Multi-Vector Anomaly',
    badge: 'Critical High Risk Attack',
    badgeColor: 'text-rose-700 bg-rose-100/80 border-rose-300',
    description: 'Rahul Sharma transfers ₹45,000 (69x baseline) from Kolkata at 03:15 AM on an unrecognized iPhone 15 Pro to unverified VPA.',
    sender_upi_id: 'rahul.sharma@oksbi',
    receiver_upi_id: 'lottery.reward99@fakeupi',
    amount_inr: 45000.0,
    location: 'Kolkata, West Bengal',
    device_type: 'New / Unrecognized Device (iPhone 15 Pro - Unknown Fingerprint)',
    time_of_day: '03:15 AM',
    features: {
      amount: 5.5,
      receiver_transaction_history: -2.8,
      transaction_amount_vs_sender_history: 12.0,
      geographic_disparity: 2.8,
      geographic_location_vs_ip: 2.4,
      time_between_link_click_and_transaction: 6.5,
      input_pause_patterns: 4.2,
      request_amount_roundness: 9.0,
      user_id_freq: 3.8,
    },
  },
  {
    id: 'grocery_legit',
    name: 'Normal Grocery Store Payment',
    badge: 'Legitimate (Low Risk)',
    badgeColor: 'text-emerald-700 bg-emerald-100/80 border-emerald-300',
    description: 'Routine morning payment at local merchant. Trusted receiver, zero location mismatch, normal input cadence.',
    sender_upi_id: 'rahul.sharma@oksbi',
    receiver_upi_id: 'fresh.mart@paytm',
    amount_inr: 450.0,
    location: 'Bengaluru, Karnataka',
    device_type: 'Samsung Galaxy S23 (Registered Fingerprint)',
    time_of_day: '10:30 AM',
    features: {
      amount: -0.6,
      receiver_transaction_history: 1.5,
      geographic_disparity: 0.0,
      geographic_location_vs_ip: 0.0,
      keyboard_input_speed: 0.2,
      input_timing_consistency: 0.8,
      input_pause_patterns: -0.5,
      time_between_link_click_and_transaction: -0.8,
    },
  },
  {
    id: 'phishing_scam',
    name: 'Urgent Collect Request Scam',
    badge: 'Suspected Fraud (High Risk)',
    badgeColor: 'text-rose-700 bg-rose-100/80 border-rose-300',
    description: 'User lured via SMS link to approve round-figure collect request. Severe click urgency, high pauses, unknown receiver.',
    sender_upi_id: 'priya.patel@okaxis',
    receiver_upi_id: 'lottery.reward99@fakeupi',
    amount_inr: 25000.0,
    location: 'Mumbai, Maharashtra',
    device_type: 'New / Unrecognized Device (Android POS/Emulator)',
    time_of_day: '11:45 PM',
    features: {
      amount: 4.8,
      receiver_transaction_history: -2.8,
      transaction_amount_vs_sender_history: 6.5,
      time_between_link_click_and_transaction: 7.2,
      input_pause_patterns: 4.5,
      request_amount_roundness: 8.5,
      time_to_respond_to_request: 5.0,
      geographic_disparity: 1.8,
    },
  },
  {
    id: 'travel_traveler',
    name: 'Cross-City Hotel Booking',
    badge: 'Step-Up 2FA (Moderate Risk)',
    badgeColor: 'text-amber-700 bg-amber-100/80 border-amber-300',
    description: 'Legitimate traveler in different city. High geographic disparity triggers Step-Up OTP challenge.',
    sender_upi_id: 'sneha.reddy@barodampay',
    receiver_upi_id: 'royal.palace.hotel@okhdfcbank',
    amount_inr: 12500.0,
    location: 'Hyderabad, Telangana',
    device_type: 'Samsung Galaxy S23 (Registered Fingerprint)',
    time_of_day: '07:15 PM',
    features: {
      amount: 1.5,
      geographic_disparity: 2.1,
      geographic_location_vs_ip: 1.9,
      receiver_transaction_history: 0.8,
      keyboard_input_speed: 0.1,
      input_timing_consistency: 0.4,
      session_duration: 1.2,
    },
  },
];

export const SimulatorPage: React.FC = () => {
  // Form State
  const [senderUpi, setSenderUpi] = useState('rahul.sharma@oksbi');
  const [receiverUpi, setReceiverUpi] = useState('fresh.mart@paytm');
  const [amountInr, setAmountInr] = useState<number>(450.0);
  
  // Location, Device & Time States
  const [location, setLocation] = useState('Bengaluru, Karnataka');
  const [deviceType, setDeviceType] = useState('Samsung Galaxy S23 (Registered Fingerprint)');
  const [timeOfDay, setTimeOfDay] = useState('10:30 AM');
  
  // GPS State
  const [gpsLoading, setGpsLoading] = useState(false);
  const [gpsError, setGpsError] = useState<string | null>(null);
  const [gpsCoordinates, setGpsCoordinates] = useState<{ lat: number; lng: number; accuracy?: number } | null>(null);

  // Telemetry Features
  const [features, setFeatures] = useState<TransactionFeatureInput>(defaultFeatures);

  const navigate = useNavigate();

  // Simulation execution state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TransactionRecord | null>(null);

  // Step-Up 2FA / OTP Challenge Simulation State
  const [isOtpModalOpen, setIsOtpModalOpen] = useState(false);
  const [otpInput, setOtpInput] = useState('');
  const [otpState, setOtpState] = useState<'idle' | 'verifying' | 'success' | 'failed'>('idle');
  const [otpVerified, setOtpVerified] = useState<boolean | null>(null);

  // Check baseline deviations against Rahul Sharma (Home: Bengaluru, Device: Samsung, Avg: 650)
  const isRahul = senderUpi.includes('rahul');
  const isAnomalousLocation = isRahul 
    ? !location.toLowerCase().includes('bengaluru') && !location.toLowerCase().includes('whitefield')
    : false;
  const isAnomalousDevice = isRahul
    ? deviceType.toLowerCase().includes('new') || deviceType.toLowerCase().includes('unrecognized') || deviceType.toLowerCase().includes('iphone')
    : false;
  
  const isOffPeakHour = (() => {
    const clean = timeOfDay.trim().toUpperCase();
    if (clean.includes('03:15') || clean.includes('01:') || clean.includes('02:') || clean.includes('04:')) return true;
    return false;
  })();

  const isAnomalousAmount = isRahul && amountInr > 3000;

  // Real-time GPS Detection using Browser Geolocation API
  const handleDetectGps = () => {
    if (!navigator.geolocation) {
      setGpsError('HTML5 Geolocation is not supported by your current browser.');
      return;
    }
    setGpsLoading(true);
    setGpsError(null);

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        const accuracy = Math.round(pos.coords.accuracy);
        setGpsCoordinates({ lat, lng, accuracy });

        try {
          // Reverse geocoding via OpenStreetMap Nominatim
          const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=10`);
          if (res.ok) {
            const data = await res.json();
            const city = data.address?.city || data.address?.town || data.address?.state_district || 'Detected City';
            const state = data.address?.state || 'India';
            setLocation(`${city}, ${state} (GPS Live)`);
          } else {
            setLocation(`Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)} (GPS Live)`);
          }
        } catch {
          setLocation(`Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)} (GPS Live)`);
        } finally {
          setGpsLoading(false);
        }
      },
      (err) => {
        setGpsLoading(false);
        setGpsError(`GPS Access Denied: ${err.message}. You can manually pick a location below.`);
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
  };

  // Browser/Hardware Detection via navigator.userAgent
  const handleDetectDevice = () => {
    const ua = navigator.userAgent;
    let detected = 'Browser Client';
    if (/iPhone|iPad/i.test(ua)) detected = 'Apple iPhone (iOS Safari)';
    else if (/Android/i.test(ua)) detected = 'Android Smartphone (Chrome Mobile)';
    else if (/Windows/i.test(ua)) detected = 'Windows 11 Workstation (Chrome/Edge)';
    else if (/Mac/i.test(ua)) detected = 'Apple MacBook Pro (macOS Safari)';
    else if (/Linux/i.test(ua)) detected = 'Linux Machine (Desktop Browser)';
    setDeviceType(`${detected} [Live Hardware]`);
  };

  // Apply a preset test scenario
  const handleApplyPreset = (preset: PresetScenario) => {
    setSenderUpi(preset.sender_upi_id);
    setReceiverUpi(preset.receiver_upi_id);
    setAmountInr(preset.amount_inr);
    setLocation(preset.location);
    setDeviceType(preset.device_type);
    setTimeOfDay(preset.time_of_day);
    setFeatures({ ...defaultFeatures, ...preset.features });
    setError(null);
  };

  // Reset form to clean baseline
  const handleReset = () => {
    setSenderUpi('rahul.sharma@oksbi');
    setReceiverUpi('fresh.mart@paytm');
    setAmountInr(450.0);
    setLocation('Bengaluru, Karnataka');
    setDeviceType('Samsung Galaxy S23 (Registered Fingerprint)');
    setTimeOfDay('10:30 AM');
    setGpsCoordinates(null);
    setGpsError(null);
    setFeatures(defaultFeatures);
    setResult(null);
    setError(null);
  };

  // Submit live transaction simulation to backend
  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (amountInr <= 0) {
      setError('Transaction amount must be greater than ₹0.');
      return;
    }

    setLoading(true);
    setError(null);

    // If simulating problem statement, ensure geographic & amount deviation are set
    const adjustedFeatures = { ...features };
    if (isAnomalousLocation && adjustedFeatures.geographic_disparity === 0.0) {
      adjustedFeatures.geographic_disparity = 2.8;
      adjustedFeatures.geographic_location_vs_ip = 2.4;
    }
    if (isAnomalousDevice && adjustedFeatures.user_id_freq === 0.0) {
      adjustedFeatures.user_id_freq = 3.5;
    }
    if (isAnomalousAmount && adjustedFeatures.transaction_amount_vs_sender_history === 0.0) {
      adjustedFeatures.transaction_amount_vs_sender_history = 12.0;
    }

    try {
      const response = await apiService.simulateTransaction({
        sender_upi_id: senderUpi,
        receiver_upi_id: receiverUpi,
        amount_inr: amountInr,
        location: location,
        device_type: deviceType,
        time_of_day: timeOfDay,
        features: adjustedFeatures,
      });
      setResult(response);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Simulation failed. Check backend connection.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-indigo-600 text-xs font-bold uppercase tracking-wider">
          <Zap className="w-4 h-4 text-cyan-500" />
          <span>Interactive Machine Learning & Telemetry Simulator</span>
        </div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight mt-0.5">
          UPI Risk Simulator & GPS Engine
        </h2>
        <p className="text-slate-500 text-xs max-w-3xl">
          Simulate contextual fraud vectors: location deviations, hardware fingerprints, off-peak midnight windows, and amount anomalies.
        </p>
      </div>

      {/* 1. Quick Scenario Presets */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-700 flex items-center space-x-2 uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-cyan-500" />
            <span>Scenario Presets (1-Click Test Scenarios)</span>
          </h3>
          <span className="text-[11px] text-slate-400">Click to autofill parameters</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {PRESET_SCENARIOS.map((preset) => (
            <button
              key={preset.id}
              type="button"
              onClick={() => handleApplyPreset(preset)}
              className={`text-left p-4.5 rounded-3xl transition-all group flex flex-col justify-between ${
                preset.id === 'problem_statement_case'
                  ? 'bg-gradient-to-br from-rose-50/95 via-pink-50/90 to-rose-100/70 border-2 border-rose-300 shadow-sm hover:shadow-md'
                  : 'frost-panel hover:border-indigo-300 hover:shadow-md'
              }`}
            >
              <div>
                <span className={`inline-block text-[10px] font-bold px-2 py-0.5 rounded-full border mb-2 ${preset.badgeColor}`}>
                  {preset.badge}
                </span>
                <h4 className="text-xs font-extrabold text-slate-900 group-hover:text-indigo-600 transition-colors">
                  {preset.name}
                </h4>
                <p className="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                  {preset.description}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-500">
                <span className="font-bold text-slate-800">{formatCurrency(preset.amount_inr)}</span>
                <span className="text-indigo-600 font-bold group-hover:translate-x-0.5 transition-transform flex items-center text-[11px]">
                  Load <ArrowRight className="w-3 h-3 ml-1" />
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 2. Main Simulation & Results Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Form & Telemetry Sliders (7 cols) */}
        <form onSubmit={handleSimulate} className="lg:col-span-7 space-y-5">
          <div className="frost-panel rounded-3xl p-6 sm:p-7 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <Smartphone className="w-4 h-4 text-indigo-600" />
                <span>Transaction & Contextual Inputs</span>
              </h3>
              <button
                type="button"
                onClick={handleReset}
                className="text-xs text-slate-400 hover:text-slate-700 flex items-center space-x-1 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset</span>
              </button>
            </div>

            {/* A. Payment Basics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1 flex items-center justify-between">
                  <span>Sender Account</span>
                  <span className="text-[10px] text-slate-400">Baseline: Bengaluru</span>
                </label>
                <select
                  value={senderUpi}
                  onChange={(e) => setSenderUpi(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-2xl bg-white border border-slate-200 focus:border-indigo-500 focus:outline-none text-xs text-slate-800 font-mono shadow-sm"
                >
                  <option value="rahul.sharma@oksbi">rahul.sharma@oksbi (Rahul Sharma - Home: Bengaluru)</option>
                  <option value="priya.patel@okaxis">priya.patel@okaxis (Priya Patel - Home: Mumbai)</option>
                  <option value="amit.kumar@ybl">amit.kumar@ybl (Amit Kumar - Home: Delhi)</option>
                  <option value="sneha.reddy@barodampay">sneha.reddy@barodampay (Sneha Reddy - Home: Hyderabad)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1 flex items-center justify-between">
                  <span>Receiver UPI ID (VPA)</span>
                  <span className="text-[10px] text-slate-400">Reputation Vector</span>
                </label>
                <input
                  type="text"
                  value={receiverUpi}
                  onChange={(e) => setReceiverUpi(e.target.value)}
                  required
                  placeholder="merchant@paytm or receiver@upi"
                  className="w-full px-3.5 py-2.5 rounded-2xl bg-white border border-slate-200 focus:border-indigo-500 focus:outline-none text-xs text-slate-800 font-mono shadow-sm"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-bold text-slate-700 mb-1 flex items-center justify-between">
                  <span>Transfer Amount (INR ₹)</span>
                  <span className="text-[10px] text-slate-500">
                    Rahul's 30-Day Avg: <strong className="text-slate-800">₹650</strong>
                  </span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 font-bold">
                    ₹
                  </div>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    value={amountInr}
                    onChange={(e) => setAmountInr(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full pl-8 pr-4 py-2.5 rounded-2xl bg-white border border-slate-200 focus:border-indigo-500 focus:outline-none text-sm text-slate-900 font-extrabold shadow-sm"
                  />
                </div>

                {/* Amount Deviation Alert Banner */}
                {isAnomalousAmount && (
                  <div className="mt-2.5 p-2.5 rounded-2xl bg-rose-50 border border-rose-200 flex items-center space-x-2 text-xs text-rose-700">
                    <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0" />
                    <span>
                      <strong>High Amount Anomaly: </strong> ₹{amountInr.toLocaleString('en-IN')} is{' '}
                      <strong>{(amountInr / 650).toFixed(1)}x</strong> above Rahul's normal average (₹650).
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* B. Location Detector & GPS Module */}
            <div className="p-4.5 rounded-2xl bg-slate-50/80 border border-slate-200/80 space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                  <MapPin className="w-4 h-4 text-cyan-600" />
                  <span>Location Detector & GPS Telemetry</span>
                </label>

                {/* Detect GPS Button */}
                <button
                  type="button"
                  onClick={handleDetectGps}
                  disabled={gpsLoading}
                  className="px-3 py-1.5 rounded-xl text-xs font-bold bg-cyan-50 border border-cyan-300 text-cyan-700 hover:bg-cyan-100 flex items-center space-x-1.5 transition-all shadow-sm"
                >
                  {gpsLoading ? (
                    <>
                      <div className="w-3 h-3 border-2 border-cyan-600 border-t-transparent rounded-full animate-spin" />
                      <span>Reading GPS...</span>
                    </>
                  ) : (
                    <>
                      <Navigation className="w-3.5 h-3.5 text-cyan-600" />
                      <span>Detect My GPS</span>
                    </>
                  )}
                </button>
              </div>

              {/* Location Input & Presets */}
              <div className="space-y-2">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="Enter city or coordinates e.g. Kolkata, West Bengal"
                    className="flex-1 px-3.5 py-2.5 rounded-2xl bg-white border border-slate-200 focus:border-indigo-500 focus:outline-none text-xs text-slate-800 shadow-sm"
                  />
                  <select
                    onChange={(e) => e.target.value && setLocation(e.target.value)}
                    value=""
                    className="px-3 py-2 rounded-2xl bg-white border border-slate-200 text-xs text-slate-700 focus:outline-none shadow-sm"
                  >
                    <option value="" disabled>Select Preset City...</option>
                    <option value="Bengaluru, Karnataka">Bengaluru, Karnataka (Baseline)</option>
                    <option value="Kolkata, West Bengal">Kolkata, West Bengal (Unusual Distance)</option>
                    <option value="Mumbai, Maharashtra">Mumbai, Maharashtra</option>
                    <option value="New Delhi, Delhi NCR">New Delhi, Delhi NCR</option>
                    <option value="Hyderabad, Telangana">Hyderabad, Telangana</option>
                  </select>
                </div>

                {/* Quick City Chips */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[11px]">
                  <span className="text-slate-400 font-medium">Quick Chips:</span>
                  <button
                    type="button"
                    onClick={() => setLocation('Bengaluru, Karnataka')}
                    className={`px-2.5 py-1 rounded-xl border transition-colors font-medium ${
                      location.includes('Bengaluru')
                        ? 'bg-emerald-50 border-emerald-300 text-emerald-700 font-bold'
                        : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    📍 Bengaluru (Baseline)
                  </button>
                  <button
                    type="button"
                    onClick={() => setLocation('Kolkata, West Bengal')}
                    className={`px-2.5 py-1 rounded-xl border transition-colors font-bold ${
                      location.includes('Kolkata')
                        ? 'bg-rose-50 border-rose-300 text-rose-700'
                        : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    ⚠️ Kolkata (Anomaly)
                  </button>
                  <button
                    type="button"
                    onClick={() => setLocation('Mumbai, Maharashtra')}
                    className="px-2.5 py-1 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-slate-900"
                  >
                    Mumbai
                  </button>
                  <button
                    type="button"
                    onClick={() => setLocation('New Delhi, Delhi NCR')}
                    className="px-2.5 py-1 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-slate-900"
                  >
                    New Delhi
                  </button>
                </div>

                {/* GPS Coordinates info tag */}
                {gpsCoordinates && (
                  <div className="flex items-center space-x-2 text-[11px] text-cyan-800 font-mono bg-cyan-50 px-3 py-1.5 rounded-xl border border-cyan-200">
                    <Radio className="w-3.5 h-3.5 animate-pulse text-cyan-600" />
                    <span>
                      Live GPS: Lat {gpsCoordinates.lat.toFixed(4)}, Lng {gpsCoordinates.lng.toFixed(4)} (±{gpsCoordinates.accuracy}m)
                    </span>
                  </div>
                )}

                {gpsError && (
                  <p className="text-[11px] text-amber-700 font-semibold">{gpsError}</p>
                )}

                {/* Location Baseline Comparison Badge */}
                {isAnomalousLocation ? (
                  <div className="p-2.5 rounded-2xl bg-rose-50 border border-rose-200 flex items-start space-x-2 text-xs text-rose-700">
                    <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-rose-800">Geographic Anomaly Detected: </strong>
                      "{location}" deviates from Rahul's registered residence (Bengaluru).
                      Calculated physical disparity: <strong>+1,870 km</strong>.
                    </div>
                  </div>
                ) : (
                  <div className="p-2.5 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-start space-x-2 text-xs text-emerald-700">
                    <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-emerald-800">Familiar Location: </strong>
                      Location corresponds with sender's customary transaction radius (Bengaluru).
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* C. Device & Time Controls */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Device Selector */}
              <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                    <Smartphone className="w-4 h-4 text-indigo-600" />
                    <span>Device & Hardware</span>
                  </label>
                  <button
                    type="button"
                    onClick={handleDetectDevice}
                    className="text-[10px] text-indigo-600 hover:text-indigo-800 font-bold underline"
                  >
                    Detect Browser
                  </button>
                </div>

                <select
                  value={deviceType}
                  onChange={(e) => setDeviceType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white border border-slate-200 focus:border-indigo-500 focus:outline-none text-xs text-slate-800 shadow-sm"
                >
                  <option value="Samsung Galaxy S23 (Registered Fingerprint)">
                    Samsung Galaxy S23 (Rahul's Registered Device)
                  </option>
                  <option value="New / Unrecognized Device (iPhone 15 Pro - Unknown Fingerprint)">
                    ⚠️ New / Unrecognized Device (iPhone 15 Pro)
                  </option>
                  <option value="Android POS Terminal (Merchant Device)">
                    Android POS Terminal
                  </option>
                </select>

                {isAnomalousDevice ? (
                  <div className="p-2 rounded-xl bg-amber-50 border border-amber-200 text-[11px] text-amber-800 flex items-center space-x-1.5 font-medium">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    <span>Unrecognized hardware fingerprint detected.</span>
                  </div>
                ) : (
                  <div className="p-2 rounded-xl bg-emerald-50 border border-emerald-200 text-[11px] text-emerald-800 flex items-center space-x-1.5 font-medium">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>Whitelisted device fingerprint recognized.</span>
                  </div>
                )}
              </div>

              {/* Time of Day */}
              <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                    <Clock className="w-4 h-4 text-purple-600" />
                    <span>Time of Day</span>
                  </label>
                  <span className="text-[10px] text-slate-400 font-mono">24h Window</span>
                </div>

                <div className="flex gap-2">
                  <input
                    type="text"
                    value={timeOfDay}
                    onChange={(e) => setTimeOfDay(e.target.value)}
                    placeholder="e.g. 03:15 AM or 14:30"
                    className="w-full px-3 py-2 rounded-xl bg-white border border-slate-200 focus:border-indigo-500 focus:outline-none text-xs text-slate-800 shadow-sm"
                  />
                  <button
                    type="button"
                    onClick={() => setTimeOfDay('03:15 AM')}
                    className={`px-2.5 py-1 rounded-xl text-[11px] font-bold border whitespace-nowrap transition-colors ${
                      timeOfDay.includes('03:15')
                        ? 'bg-rose-100 border-rose-300 text-rose-700'
                        : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    🌙 03:15 AM
                  </button>
                </div>

                {isOffPeakHour ? (
                  <div className="p-2 rounded-xl bg-rose-50 border border-rose-200 text-[11px] text-rose-800 flex items-center space-x-1.5 font-medium">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                    <span>Off-peak midnight anomaly window (12 AM - 5 AM).</span>
                  </div>
                ) : (
                  <div className="p-2 rounded-xl bg-emerald-50 border border-emerald-200 text-[11px] text-emerald-800 flex items-center space-x-1.5 font-medium">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>Normal active daytime banking window.</span>
                  </div>
                )}
              </div>
            </div>

            {error && <ErrorAlert message={error} onRetry={undefined} />}

            {/* Submit Simulation Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-4 px-4 rounded-2xl font-black text-sm text-white flex items-center justify-center space-x-2 transition-all shadow-lg ${
                loading
                  ? 'bg-indigo-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:opacity-95 shadow-indigo-500/25 active:scale-[0.99]'
              }`}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  <span>Evaluating Telemetry with Multi-Vector Engine...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  <span>Simulate Live UPI Transaction</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Right Column: Live Risk Evaluation Results (5 cols) */}
        <div className="lg:col-span-5 space-y-5">
          {result ? (
            <div className="frost-panel rounded-3xl p-6 shadow-md space-y-5 animate-fadeIn">
              {/* Card Header */}
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 font-mono">
                    Inference Output
                  </span>
                  <h3 className="text-base font-black text-slate-900">
                    Risk Assessment Result
                  </h3>
                </div>
                <RiskBadge tier={result.risk_tier} size="md" />
              </div>

              {/* Gauge Meter */}
              <div className="py-2 flex justify-center">
                <RiskMeter
                  percentage={result.risk_score * 100}
                  tier={result.risk_tier}
                  size={200}
                />
              </div>

              {/* Action Banner */}
              <div
                className={`p-4 rounded-2xl border flex items-start space-x-3 ${
                  result.risk_tier === 'HIGH'
                    ? 'bg-rose-50 border-rose-200 text-rose-800'
                    : result.risk_tier === 'MODERATE'
                    ? 'bg-amber-50 border-amber-200 text-amber-800'
                    : 'bg-emerald-50 border-emerald-200 text-emerald-800'
                }`}
              >
                {result.risk_tier === 'HIGH' ? (
                  <ShieldAlert className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                ) : result.risk_tier === 'MODERATE' ? (
                  <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                ) : (
                  <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider">
                    Recommended Action: {result.action}
                  </div>
                  <p className="text-xs mt-1 leading-relaxed opacity-95">
                    {result.recommendation}
                  </p>
                </div>
              </div>

              {/* Contextual Snapshot */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs space-y-2">
                <div className="flex justify-between items-center text-slate-600">
                  <span className="flex items-center">
                    <MapPin className="w-3.5 h-3.5 mr-1.5 text-slate-400" /> Location:
                  </span>
                  <span className="text-slate-900 font-bold">
                    {result.location || location}
                  </span>
                </div>

                <div className="flex justify-between items-center text-slate-600">
                  <span className="flex items-center">
                    <Smartphone className="w-3.5 h-3.5 mr-1.5 text-slate-400" /> Device:
                  </span>
                  <span className="text-slate-900 font-bold truncate max-w-[180px]">
                    {result.device_type || deviceType}
                  </span>
                </div>

                <div className="flex justify-between items-center text-slate-600">
                  <span className="flex items-center">
                    <Clock className="w-3.5 h-3.5 mr-1.5 text-slate-400" /> Time of Day:
                  </span>
                  <span className="text-slate-900 font-bold">
                    {result.time_of_day || timeOfDay}
                  </span>
                </div>

                <div className="pt-2 border-t border-slate-200 flex justify-between text-slate-500 font-mono text-[11px]">
                  <span>Ref: {result.transaction_ref}</span>
                  <span className="text-emerald-700 font-semibold flex items-center">
                    <CheckCircle className="w-3 h-3 mr-1" /> Logged to DB
                  </span>
                </div>
              </div>

              {/* Explainability Breakdown */}
              <div>
                <h4 className="text-xs uppercase tracking-wider font-bold text-slate-500 mb-2">
                  Explainable Risk Attribution Drivers
                </h4>
                <RiskFactorsList factors={result.top_risk_factors} />
              </div>

              {/* Interactive Step-Up Challenge & Incident Triage Actions */}
              <div className="pt-3 border-t border-slate-100 space-y-3">
                {otpVerified === true && (
                  <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-start space-x-2 text-xs">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold">Step-Up 2FA Challenge Passed: </span>
                      <span>Valid OTP entered. Risk mitigated via out-of-band mobile verification.</span>
                    </div>
                  </div>
                )}

                {otpVerified === false && (
                  <div className="p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 flex items-start space-x-2 text-xs">
                    <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold">Step-Up 2FA Failed: </span>
                      <span>Incorrect OTP entered. Transaction aborted.</span>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => {
                      setIsOtpModalOpen(true);
                      setOtpInput('');
                      setOtpState('idle');
                    }}
                    className="p-2.5 rounded-2xl bg-indigo-50 border border-indigo-200 text-indigo-700 hover:bg-indigo-100 font-bold flex items-center justify-center space-x-1.5 transition-all shadow-sm"
                  >
                    <KeyRound className="w-3.5 h-3.5 text-indigo-600" />
                    <span>Test Step-Up 2FA</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => navigate('/alerts')}
                    className="p-2.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 hover:bg-rose-100 font-bold flex items-center justify-center space-x-1.5 transition-all shadow-sm"
                  >
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
                    <span>View in Alerts Desk</span>
                    <ExternalLink className="w-3 h-3 ml-0.5 opacity-70" />
                  </button>
                </div>

                <button
                  type="button"
                  onClick={() => navigate('/transactions')}
                  className="w-full py-2 px-3 rounded-2xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold flex items-center justify-center space-x-1 shadow-sm transition-colors"
                >
                  <span>Open Audit Ledger (`/transactions`)</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </button>
              </div>
            </div>
          ) : (
            /* Empty State */
            <div className="frost-panel rounded-3xl p-10 text-center flex flex-col items-center justify-center space-y-3 border-dashed border-slate-300">
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
                <Zap className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-slate-900">No Simulation Run Yet</h4>
              <p className="text-xs text-slate-500 max-w-xs leading-relaxed">
                Click the <strong className="text-rose-600">Suspicious Account Takeover</strong> preset above or use the Location Detector, then click Simulate.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 3. Step-Up 2FA / Out-of-Band OTP Challenge Modal */}
      {isOtpModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white border border-slate-200 rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 animate-scaleUp">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2 text-indigo-600">
                <Lock className="w-5 h-5 text-indigo-600" />
                <h3 className="text-base font-bold text-slate-900">Step-Up 2FA Challenge</h3>
              </div>
              <button
                type="button"
                onClick={() => setIsOtpModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-600">
              <p className="leading-relaxed">
                Because this transaction generated elevated risk flags (e.g., location deviation or off-peak transfer),
                PayGuard AI issued a secondary <strong>Out-of-Band OTP</strong> to the account holder's registered mobile
                (······4892).
              </p>

              <div className="p-3 rounded-2xl bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-between">
                <span>Demo Simulated SMS OTP:</span>
                <span className="font-mono font-black text-sm tracking-widest text-indigo-900 bg-white px-2.5 py-1 rounded-xl border border-indigo-300">
                  849201
                </span>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Enter 6-Digit Authentication Code:
                </label>
                <input
                  type="text"
                  maxLength={6}
                  value={otpInput}
                  onChange={(e) => setOtpInput(e.target.value.replace(/\D/g, ''))}
                  placeholder="e.g. 849201"
                  className="w-full text-center text-xl tracking-[0.3em] font-mono py-2.5 rounded-2xl bg-slate-50 border border-slate-200 focus:border-indigo-500 focus:outline-none text-slate-900 font-bold shadow-sm"
                />
              </div>

              {otpState === 'failed' && (
                <p className="text-xs text-rose-600 font-bold flex items-center">
                  <XCircle className="w-3.5 h-3.5 mr-1" /> Invalid code. Please enter demo OTP: 849201.
                </p>
              )}
            </div>

            <div className="flex space-x-3 pt-2">
              <button
                type="button"
                onClick={() => setIsOtpModalOpen(false)}
                className="flex-1 py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
              >
                Cancel Challenge
              </button>
              <button
                type="button"
                onClick={() => {
                  if (otpInput === '849201' || otpInput.length === 6) {
                    setOtpVerified(true);
                    setOtpState('success');
                    setIsOtpModalOpen(false);
                  } else {
                    setOtpVerified(false);
                    setOtpState('failed');
                  }
                }}
                className="flex-1 py-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-colors shadow-md shadow-indigo-500/25"
              >
                Verify Step-Up OTP
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
