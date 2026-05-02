# Vōgue·AI — Frontend

Next.js 14 + TypeScript frontend for the Fashion Trend AI platform.

## Tech Stack
- **Framework**: Next.js 14 App Router
- **Styling**: Tailwind CSS + custom CSS variables
- **Charts**: Recharts
- **State**: Zustand
- **HTTP**: Axios with JWT interceptors
- **Fonts**: Cormorant Garamond (serif) + DM Sans (sans)
- **Icons**: Lucide React

## Pages
| Route | Page |
|-------|------|
| `/dashboard` | Stats, agents, trend table, charts |
| `/trends` | Full trend list with filters & sparklines |
| `/predictions` | Season forecasts + model comparison charts |
| `/agents` | 5 AI agent status cards |
| `/colors` | Color palette explorer |
| `/advisor` | Claude-powered AI chat |
| `/reports` | Report generation & download |
| `/subscription` | Pricing plans |
| `/login` | Auth |
| `/register` | Sign up |

## Quick Start

\`\`\`bash
cd fashion-frontend
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL to your backend URL

npm install
npm run dev        # → http://localhost:3000
\`\`\`

## Connect to Backend
Edit `.env.local`:
\`\`\`
NEXT_PUBLIC_API_URL=http://localhost:8000
\`\`\`
Make sure the FastAPI backend is running on port 8000.

## Build for Production
\`\`\`bash
npm run build
npm start
\`\`\`

## Design System
Dark editorial luxury theme:
- **Background**: `#0A0A0F`
- **Surface**: `#111118`
- **Card**: `#16161F`
- **Border**: `#1E1E2E`
- **Gold accent**: `#C9A96E`
- **Rose**: `#D4688A`
- **Teal**: `#4ECDC4`
- **Jade**: `#52C97A`

---

## 💳 Payment Integration

### Frontend Payment Pages
| Route | Component | Description |
|-------|-----------|-------------|
| `/subscription` | `SubscriptionPage` | Plan comparison (monthly/yearly toggle) |
| `/checkout` | `CheckoutPage` | Plan selector + Stripe Checkout redirect |
| `/checkout/success` | `CheckoutSuccessPage` | Post-payment confirmation |
| `/billing` | `BillingPage` | Full account: invoices, cards, upgrade, cancel |

### Payment Flow
```
User clicks "Start Free Trial"
  → /checkout (select plan)
  → POST /api/v1/payments/checkout-session
  → Redirect to Stripe Checkout (hosted)
  → Stripe redirects to /checkout/success?session_id=cs_xxx
  → GET /api/v1/payments/checkout-session/cs_xxx (verify)
  → Show confirmation → redirect to /dashboard
```

### Billing Page Features
- Current subscription status with color-coded indicator
- One-click plan upgrade/downgrade with proration
- Open Stripe Billing Portal (manage cards, download invoices)
- Invoice history with PDF download links
- Saved payment methods display
- Cancel / reactivate subscription

### Environment Variables (Frontend)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000   # Backend URL
```
The frontend does NOT need a Stripe public key — all Stripe calls go through the backend.
