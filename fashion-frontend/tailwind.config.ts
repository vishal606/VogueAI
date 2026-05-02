import type { Config } from 'tailwindcss'
const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      fontFamily: {
        serif: ['var(--font-cormorant)', 'Georgia', 'serif'],
        sans: ['var(--font-dm-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-dm-mono)', 'monospace'],
      },
      colors: {
        ink: { DEFAULT: '#0A0A0F', 50: '#f0eee8', 100: '#e0ddd0', 200: '#c4bfac', 300: '#a09880', 400: '#6B6B7A', 500: '#48484F', 600: '#2A2A32', 700: '#1E1E2E', 800: '#16161F', 900: '#111118', 950: '#0A0A0F' },
        gold: { DEFAULT: '#C9A96E', light: '#DCC08E', dark: '#8B6F47', muted: 'rgba(201,169,110,0.12)' },
        rose: { DEFAULT: '#D4688A', muted: 'rgba(212,104,138,0.12)' },
        teal: { DEFAULT: '#4ECDC4', muted: 'rgba(78,205,196,0.12)' },
        violet: { DEFAULT: '#7C5CBF', muted: 'rgba(124,92,191,0.12)' },
        jade: { DEFAULT: '#52C97A', muted: 'rgba(82,201,122,0.12)' },
      },
      backgroundImage: {
        'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E\")",
        'gold-gradient': 'linear-gradient(135deg, #C9A96E 0%, #DCC08E 50%, #8B6F47 100%)',
        'hero-gradient': 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(201,169,110,0.15) 0%, transparent 70%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease forwards',
        'slide-up': 'slideUp 0.5s cubic-bezier(0.16,1,0.3,1) forwards',
        'slide-in-right': 'slideInRight 0.4s cubic-bezier(0.16,1,0.3,1) forwards',
        'ticker': 'ticker 28s linear infinite',
        'pulse-gold': 'pulseGold 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'spin-slow': 'spin 8s linear infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(20px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        slideInRight: { from: { opacity: '0', transform: 'translateX(20px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
        ticker: { from: { transform: 'translateX(0)' }, to: { transform: 'translateX(-50%)' } },
        pulseGold: { '0%,100%': { opacity: '1', boxShadow: '0 0 0 0 rgba(201,169,110,0.4)' }, '50%': { opacity: '0.7', boxShadow: '0 0 0 6px rgba(201,169,110,0)' } },
        shimmer: { from: { backgroundPosition: '-200% 0' }, to: { backgroundPosition: '200% 0' } },
        float: { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-8px)' } },
      },
      boxShadow: {
        'gold': '0 0 20px rgba(201,169,110,0.25)',
        'gold-lg': '0 0 40px rgba(201,169,110,0.3)',
        'card': '0 4px 24px rgba(0,0,0,0.4)',
        'card-hover': '0 12px 40px rgba(0,0,0,0.6)',
        'inner-gold': 'inset 0 1px 0 rgba(201,169,110,0.15)',
      },
      borderColor: { DEFAULT: 'rgba(30,30,46,1)' },
    },
  },
  plugins: [],
}
export default config
