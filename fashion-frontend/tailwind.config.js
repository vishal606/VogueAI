/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#08080E',
        surface: '#0F0F18',
        card: '#13131E',
        border: '#1C1C2E',
        accent: '#C9A96E',
        'accent-soft': '#8B6F47',
        'accent-dim': 'rgba(201,169,110,0.08)',
        rose: '#D4688A',
        teal: '#4ECDC4',
        purple: '#7C5CBF',
        success: '#52C97A',
        muted: '#5A5A72',
        subtle: '#3A3A52',
      },
      fontFamily: {
        display: ['var(--font-cormorant)', 'Georgia', 'serif'],
        body: ['var(--font-dm-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains)', 'monospace'],
      },
      fontSize: {
        '2xs': ['10px', { letterSpacing: '0.08em' }],
        xs: ['11px', { letterSpacing: '0.06em' }],
        sm: ['12px', { letterSpacing: '0.02em' }],
        base: ['13px', { letterSpacing: '0.01em' }],
        md: ['14px', {}],
        lg: ['16px', {}],
        xl: ['18px', {}],
        '2xl': ['22px', {}],
        '3xl': ['28px', {}],
        '4xl': ['36px', {}],
        '5xl': ['48px', {}],
        '6xl': ['64px', {}],
        '7xl': ['80px', {}],
      },
      spacing: {
        18: '72px',
        22: '88px',
        30: '120px',
      },
      borderRadius: {
        sm: '4px',
        DEFAULT: '8px',
        md: '10px',
        lg: '14px',
        xl: '20px',
        '2xl': '28px',
      },
      boxShadow: {
        glow: '0 0 24px rgba(201,169,110,0.15)',
        'glow-sm': '0 0 12px rgba(201,169,110,0.1)',
        deep: '0 24px 64px rgba(0,0,0,0.6)',
        card: '0 4px 24px rgba(0,0,0,0.4)',
      },
      animation: {
        'fade-up': 'fadeUp 0.5s ease forwards',
        'fade-in': 'fadeIn 0.4s ease forwards',
        ticker: 'ticker 30s linear infinite',
        pulse: 'pulse 2s ease-in-out infinite',
        shimmer: 'shimmer 1.8s linear infinite',
        float: 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeUp: {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        ticker: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E\")",
      },
      transitionTimingFunction: {
        'out-expo': 'cubic-bezier(0.19, 1, 0.22, 1)',
        'in-out-expo': 'cubic-bezier(0.87, 0, 0.13, 1)',
      },
    },
  },
  plugins: [],
}
