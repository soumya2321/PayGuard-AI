/**
 * demoUsers.ts - Pre-configured demo accounts for academic testing and presentation.
 * All passwords conform to the strict security policy:
 * (8+ characters, at least 1 uppercase letter, 1 number, and 1 special symbol).
 */

import type { DemoUserAccount } from '../types/auth.types';

export const DEMO_USERS: readonly DemoUserAccount[] = [
  {
    name: 'Rahul Sharma',
    email: 'rahul.sharma@oksbi',
    password: 'Customer#2026',
    role: 'customer',
    description: 'Personal banking customer with baseline routine daily UPI spends.',
  },
  {
    name: 'Fresh Mart Merchant',
    email: 'fresh.mart@paytm',
    password: 'Merchant#2026',
    role: 'merchant',
    description: 'Registered verified merchant account accepting daily P2M payments.',
  },
  {
    name: 'Vikram Singh (Security Analyst)',
    email: 'analyst@payguard.ai',
    password: 'Admin@Secure2026',
    role: 'admin',
    description: 'System administrator with full surveillance, alert triage, and override permissions.',
  },
] as const;
