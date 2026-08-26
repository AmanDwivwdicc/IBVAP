/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ibvap: {
          bg: '#0a0e17',
          panel: '#111827',
          border: '#1f2937',
          accent: '#06b6d4',
          critical: '#ef4444',
          warning: '#f59e0b',
          info: '#3b82f6',
          success: '#22c55e',
          muted: '#6b7280',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
