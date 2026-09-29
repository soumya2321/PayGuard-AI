/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        cyber: {
          bg: '#080f22',
          card: '#0d1836',
          sidebar: '#1f133d',
          sidebarLight: '#2c1a52',
          cyan: '#06b6d4',
          sky: '#38bdf8',
          blue: '#3b82f6',
          purple: '#8b5cf6',
          pink: '#ec4899',
          magenta: '#f43f5e',
        },
        frost: {
          canvas: '#e9eff8',
          card: '#ffffff',
          cardMuted: '#f8fafc',
          border: 'rgba(255, 255, 255, 0.8)',
          text: '#1e293b',
          muted: '#64748b',
        },
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          900: '#1e1b4b',
        },
        risk: {
          low: '#10b981',
          moderate: '#f59e0b',
          high: '#ef4444',
        }
      },
      boxShadow: {
        'glow-cyan': '0 0 35px -5px rgba(6, 182, 212, 0.35)',
        'glow-pink': '0 0 35px -5px rgba(236, 72, 153, 0.35)',
        'glow-blue': '0 0 35px -5px rgba(59, 130, 246, 0.4)',
        'console': '0 25px 80px -15px rgba(4, 18, 48, 0.65)',
        'frost-card': '0 4px 20px -2px rgba(15, 23, 42, 0.05)',
      },
      borderRadius: {
        '3xl': '1.75rem',
        '4xl': '2.25rem',
      }
    },
  },
  plugins: [],
}
