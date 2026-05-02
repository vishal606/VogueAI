# 🧵 Fashion Trend AI — Complete Project Documentation

> **AI-Powered Fashion Trend Prediction Platform**  
> A full-stack SaaS product for boutique owners and fashion brands.  
> Multi-agent AI system · FastAPI backend · Next.js frontend · Stripe payments

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Database Schema (ER Diagram)](#5-database-schema)
6. [Multi-Agent AI System](#6-multi-agent-ai-system)
7. [Backend Setup](#7-backend-setup)
8. [Frontend Setup](#8-frontend-setup)
9. [Environment Variables](#9-environment-variables)
10. [API Reference](#10-api-reference)
11. [Payment Gateway (Stripe)](#11-payment-gateway)
12. [Subscription Plans](#12-subscription-plans)
13. [Background Workers & Scheduling](#13-background-workers)
14. [Frontend Pages](#14-frontend-pages)
15. [UI Design System](#15-ui-design-system)
16. [Docker Deployment](#16-docker-deployment)
17. [Testing](#17-testing)
18. [Database Migrations](#18-database-migrations)
19. [Required API Keys](#19-required-api-keys)
20. [Production Deployment](#20-production-deployment)

---

## 1. Project Overview

Fashion Trend AI is a **subscription-based SaaS platform** that:

- **Scrapes** social media (Instagram, TikTok, Pinterest, Google Trends) every 15 minutes
- **Analyzes** images with computer vision (CLIP model) to extract colors, clothing types, patterns
- **Processes** captions with NLP (KeyBERT, TextBlob) to score hashtag trends and sentiment
- **Forecasts** next-season trends using a Prophet + LSTM + XGBoost ensemble
- **Advises** boutique owners with personalized inventory recommendations via Claude AI
- **Charges** users via Stripe with 14-day free trials and three subscription tiers

**Target Users:** Boutique owners · Online fashion stores · Fashion designers

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                │
│  Instagram · TikTok · Pinterest · YouTube · Google Trends           │
│  Amazon · Etsy · Daraz · Vogue · Elle · Hypebeast                  │
└────────────────────┬────────────────────────────────────────────────┘
                     │ Scrape every 15 min
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                             │
│  Data Collectors (Scrapers/Apify APIs)                              │
│  Data Streaming → Raw Data Storage → Cleaning → Metadata            │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  MULTI-AGENT AI SYSTEM                              │
│                                                                     │
│  Agent 1          Agent 2          Agent 3                          │
│  Trend Collector  Vision Analyzer  Trend Analyzer                   │
│  (Scraper)        (CLIP ViT)       (KeyBERT+NLP)                   │
│                                                                     │
│  Agent 4          Agent 5                                           │
│  Forecast Agent   Business Advisor                                  │
│  (Prophet+LSTM)   (Claude API)                                      │
│                                                                     │
│  ─────── Agent Orchestrator & Communication Layer ──────            │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                               │
│  PostgreSQL (main DB) · MongoDB (raw data) · Redis (cache/queue)   │
│  Pinecone (vector DB) · AWS S3 (files/reports)                     │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  BACKEND SERVICES LAYER (FastAPI)                   │
│  Auth · Users · Trends · Predictions · Recommendations             │
│  Alerts · Reports · Subscriptions · Payments · AI Advisor          │
│  ──────── API Gateway (REST / GraphQL) ──────────────               │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER (Next.js)                       │
│  Dashboard · Live Trends · Predictions · Color Trends              │
│  AI Advisor Chat · Reports · Billing · Subscription                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.111 + Uvicorn |
| Database | PostgreSQL 16 (async via SQLAlchemy 2.0 + asyncpg) |
| ORM | SQLAlchemy 2.0 with async sessions |
| Migrations | Alembic (async) |
| Cache / Queue | Redis 7 |
| Task Queue | Celery 5.4 + Redis broker |
| Task Monitor | Flower |
| Raw Data Store | MongoDB 7 |
| Vector Database | Pinecone |
| File Storage | AWS S3 / GCS |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| AI — Vision | CLIP ViT (HuggingFace Transformers + PyTorch) |
| AI — NLP | KeyBERT + TextBlob + custom TF-IDF |
| AI — Forecast | Prophet + PyTorch LSTM + XGBoost |
| AI — Advisor | Anthropic Claude (claude-sonnet-4-20250514) |
| Scraping | httpx + Apify API + Playwright |
| Payments | Stripe (Checkout Sessions + Webhooks) |
| Email | SendGrid |
| SMS | Twilio |
| Containerisation | Docker + Docker Compose |
| Orchestration | Kubernetes (production) |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS 3.4 + CSS custom properties |
| State | Zustand 4 |
| HTTP Client | Axios with JWT auto-refresh interceptor |
| Charts | Recharts 2 |
| Icons | Lucide React |
| Fonts | Cormorant Garamond (serif) + DM Sans (sans) |
| Notifications | react-hot-toast |
| Animation | CSS keyframes + Tailwind animations |

---

## 4. Project Structure

```
fashion-trend-ai/                    ← Backend (FastAPI)
├── app/
│   ├── main.py                      ← FastAPI factory, CORS, lifespan, plan seeding
│   ├── core/
│   │   ├── config.py                ← Pydantic Settings (all env vars)
│   │   └── security.py              ← JWT tokens, bcrypt hashing
│   ├── db/
│   │   ├── base.py                  ← Async SQLAlchemy engine + session + init_db
│   │   ├── models/models.py         ← 13 ORM models matching ER diagram
│   │   └── schemas/schemas.py       ← 40+ Pydantic v2 request/response schemas
│   ├── api/
│   │   ├── deps.py                  ← Auth guards, subscription guards, pagination
│   │   └── v1/
│   │       ├── router.py            ← Assembles all routers
│   │       └── endpoints/
│   │           ├── auth.py          ← Register, login, refresh, /me, logout
│   │           ├── users.py         ← User profile CRUD + admin list
│   │           ├── trends.py        ← Trend CRUD, filtering, sorting, dashboard
│   │           ├── predictions.py   ← Forecast generation, season forecasts
│   │           ├── recommendations.py ← AI business recommendations
│   │           ├── alerts.py        ← Custom alert rule management
│   │           ├── reports.py       ← Report generation + download
│   │           ├── subscriptions.py ← Stripe subscriptions + webhook
│   │           ├── payments.py      ← Full payment gateway (11 endpoints)
│   │           └── advisor.py       ← AI advisor chat, color trends, scraper trigger
│   ├── services/
│   │   ├── trend_service.py         ← Dashboard, scoring, report generation
│   │   ├── ai_service.py            ← All 5 agent orchestration + Claude advisor
│   │   └── recommendation_service.py ← Recommendation lifecycle management
│   ├── ai/
│   │   ├── vision_model.py          ← Agent 2: CLIP image classification
│   │   ├── nlp_model.py             ← Agent 3: NLP, hashtag, sentiment analysis
│   │   └── forecasting.py           ← Agent 4: Prophet + LSTM + XGBoost ensemble
│   ├── workers/
│   │   ├── scraper.py               ← Agent 1: Instagram, TikTok, Pinterest, Google
│   │   └── scheduler.py             ← Celery tasks + beat schedule (6 tasks)
│   └── utils/
│       ├── logger.py                ← Loguru setup (console + rotating file)
│       └── helpers.py               ← Color math, formatters, utilities
├── alembic/                         ← Database migrations
│   ├── env.py                       ← Async Alembic configuration
│   ├── script.py.mako               ← Migration template
│   └── versions/                    ← Migration files (auto-generated)
├── tests/
│   ├── conftest.py                  ← Fixtures, in-memory test DB, test users
│   ├── api/
│   │   ├── test_auth.py             ← 12 auth tests
│   │   ├── test_trends.py           ← 16 trend tests
│   │   ├── test_endpoints.py        ← Subscription/alert/report/user/rec tests
│   │   └── test_payments.py         ← 31 payment gateway tests
│   ├── ai/
│   │   └── test_ai_agents.py        ← NLP, Vision, Forecasting, Helpers tests
│   └── workers/
│       └── test_scraper.py          ← Scraper + orchestrator tests
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pytest.ini
├── requirements.txt
├── alembic.ini
├── .env.example
└── README.md

fashion-frontend/                    ← Frontend (Next.js 14)
├── src/
│   ├── app/                         ← Next.js App Router pages
│   │   ├── layout.tsx               ← Root layout with fonts + toaster
│   │   ├── page.tsx                 ← Root redirect → /dashboard
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── trends/page.tsx
│   │   ├── predictions/page.tsx
│   │   ├── agents/page.tsx
│   │   ├── colors/page.tsx
│   │   ├── advisor/page.tsx
│   │   ├── reports/page.tsx
│   │   ├── subscription/page.tsx
│   │   ├── checkout/page.tsx        ← Plan selection + Stripe redirect
│   │   ├── checkout/success/page.tsx ← Post-payment confirmation
│   │   └── billing/page.tsx         ← Full billing management
│   ├── components/
│   │   ├── ui/index.tsx             ← Button, Card, Badge, Input, StatCard, Sparkline...
│   │   ├── layout/
│   │   │   ├── AppShell.tsx         ← Sidebar + Topbar wrapper
│   │   │   ├── Sidebar.tsx          ← Collapsible nav with all routes
│   │   │   └── Topbar.tsx           ← Live ticker + agent status + refresh
│   │   ├── auth/AuthPages.tsx       ← Login + Register with editorial design
│   │   ├── dashboard/
│   │   │   ├── DashboardPage.tsx    ← Stats, agents, trend table, charts
│   │   │   └── OtherPages.tsx       ← Colors, Agents, Reports, Subscription pages
│   │   ├── trends/TrendsPage.tsx    ← Table + grid view, filtering, sparklines
│   │   ├── predictions/PredictionsPage.tsx ← Forecasts, radar chart, model cards
│   │   ├── advisor/AdvisorPage.tsx  ← Claude AI chat with context panel
│   │   └── payment/PaymentPages.tsx ← Checkout, Success, Billing pages
│   ├── lib/
│   │   ├── api.ts                   ← Full Axios client (all endpoints + JWT refresh)
│   │   ├── store.ts                 ← Zustand stores (Auth, UI, Trends, Chat)
│   │   └── utils.ts                 ← Color maps, formatters, status constants
│   ├── hooks/index.ts               ← useAuth, useDebounce, useLocalStorage
│   ├── types/index.ts               ← All TypeScript interfaces matching backend
│   └── styles/globals.css           ← Dark theme CSS, animations, components
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── next.config.js
├── postcss.config.js
├── .env.example
└── README.md
```

---

## 5. Database Schema

### Tables (13 total)

#### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | Auto-generated |
| name | VARCHAR(255) | Required |
| email | VARCHAR(255) UNIQUE | Indexed |
| password_hash | TEXT | bcrypt |
| role | VARCHAR(50) | boutique_owner / fashion_designer / online_store / admin |
| is_active | BOOLEAN | Default true |
| is_verified | BOOLEAN | Default false |
| stripe_customer_id | VARCHAR(255) | Nullable |
| created_at | TIMESTAMP | Auto |
| updated_at | TIMESTAMP | Auto |

#### `subscription_plans`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(100) | Basic / Pro / Premium |
| type | VARCHAR(50) | monthly / yearly |
| price | DECIMAL(10,2) | |
| features | JSONB | Feature flags dict |
| stripe_price_id | VARCHAR(255) | Stripe price object ID |
| is_active | BOOLEAN | |

#### `subscriptions`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| plan_id | UUID FK → subscription_plans | |
| status | VARCHAR(50) | active / canceled / past_due / trialing / pending |
| start_date | DATE | |
| end_date | DATE | Nullable |
| stripe_subscription_id | VARCHAR(255) | |

#### `sources`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(100) | Instagram / TikTok / Pinterest / YouTube / etc. |
| type | VARCHAR(50) | social_media / ecommerce / news / search_trends |
| description | TEXT | Nullable |
| is_active | BOOLEAN | |
| last_scraped_at | TIMESTAMP | Nullable |
| scrape_config | JSONB | Scraper settings |

#### `raw_posts`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| source_id | UUID FK → sources | |
| post_url | TEXT | Nullable |
| caption | TEXT | Nullable |
| image_url | TEXT | Nullable |
| video_url | TEXT | Nullable |
| likes | INT | Default 0 |
| comments | INT | Default 0 |
| shares | INT | Default 0 |
| views | INT | Default 0 |
| posted_at | TIMESTAMP | Nullable |
| scraped_at | TIMESTAMP | Auto |
| raw_data | JSONB | Full API response |
| is_processed | BOOLEAN | Default false |

#### `image_features` (Agent 2 output)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| post_id | UUID FK → raw_posts UNIQUE | One-to-one |
| dominant_color | VARCHAR(50) | Color name |
| color_palette | JSONB | [{hex, name, percentage, rgb}] |
| clothing_type | VARCHAR(100) | dress / blouse / pants / etc. |
| pattern | VARCHAR(100) | solid / striped / floral / etc. |
| style_tags | JSONB | [minimalist, luxury, ...] |
| embedding | JSONB | 512-dim CLIP vector |
| confidence | FLOAT | Model confidence 0-1 |
| model_used | VARCHAR(100) | clip-vit-base-patch32 |
| raw_predictions | JSONB | Full model output |

#### `text_features` (Agent 3 output)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| post_id | UUID FK → raw_posts UNIQUE | One-to-one |
| keywords | JSONB | Extracted keywords list |
| hashtags | JSONB | Extracted hashtags list |
| sentiment | FLOAT | -1.0 to +1.0 |
| entities | JSONB | Brands, designers |
| language | VARCHAR(10) | Default "en" |
| topics | JSONB | [Style, Color, Season, ...] |

#### `trends`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(255) INDEXED | |
| category | VARCHAR(100) | Style / Color / Texture / Accessory / Footwear |
| trend_score | FLOAT | 0-100 composite score |
| growth_rate | FLOAT | Percentage change |
| region | VARCHAR(100) | Global / Europe / Asia / Americas |
| date | DATE | |
| status | VARCHAR(50) | emerging / rising / peak / declining |
| source_breakdown | JSONB | {instagram: {score}, tiktok: ...} |
| top_hashtags | JSONB | Top associated hashtags |
| sample_images | JSONB | Sample image URLs |
| color_hex | VARCHAR(20) | Nullable |
| metadata | JSONB | Additional data |

#### `trend_predictions` (Agent 4 output)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| trend_id | UUID FK → trends | |
| predicted_value | FLOAT | Predicted score 0-100 |
| prediction_date | DATE | Future date |
| confidence | FLOAT | 0-1 |
| model_used | VARCHAR(100) | prophet / lstm / xgboost |
| horizon_days | INT | 7-365 |
| lower_bound | FLOAT | Nullable |
| upper_bound | FLOAT | Nullable |
| season | VARCHAR(100) | "Summer 2025" etc |
| factors | JSONB | Feature importance dict |

#### `recommendations` (Agent 5 output)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| trend_id | UUID FK → trends | |
| action | VARCHAR(100) | stock_now / avoid / monitor / reduce_inventory / feature_prominently |
| description | TEXT | |
| priority | VARCHAR(20) | high / medium / low |
| confidence_score | FLOAT | 0-1 |
| is_read | BOOLEAN | Default false |
| ai_reasoning | TEXT | Claude explanation |
| expires_at | TIMESTAMP | Nullable |

#### `alerts`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| trend_id | UUID FK → trends | Nullable |
| alert_type | VARCHAR(50) | trend_spike / trend_decline / new_trend / recommendation |
| threshold | FLOAT | Nullable |
| triggered | BOOLEAN | Default false |
| triggered_at | TIMESTAMP | Nullable |
| triggered_value | FLOAT | Nullable |
| channels | JSONB | [email, sms, push, in_app] |
| message | TEXT | Nullable |
| is_active | BOOLEAN | Default true |

#### `reports`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| title | VARCHAR(255) | |
| report_type | VARCHAR(100) | weekly_trends / color_palette / season_forecast / recommendations / custom |
| file_url | TEXT | S3 URL when generated |
| status | VARCHAR(50) | pending / generating / ready / failed |
| filters | JSONB | Applied filter criteria |
| data_snapshot | JSONB | Embedded report data |
| expires_at | TIMESTAMP | Nullable |

#### `competitors_tracking`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| brand_name | VARCHAR(255) INDEXED | |
| product_type | VARCHAR(100) | Nullable |
| trend_id | UUID FK → trends | |
| popularity_score | FLOAT | |
| price_range | JSONB | {min, max, avg, currency} |
| product_count | INT | |
| source_url | TEXT | Nullable |
| raw_data | JSONB | |

### Relationships
```
users ──< subscriptions >── subscription_plans
users ──< reports
users ──< recommendations >── trends
users ──< alerts >── trends
sources ──< raw_posts
raw_posts ──1:1── image_features
raw_posts ──1:1── text_features
trends ──< trend_predictions
trends ──< recommendations
trends ──< alerts
trends ──< competitors_tracking
```

---

## 6. Multi-Agent AI System

### Agent 1: Trend Collector (`app/workers/scraper.py`)
**Role:** Collects raw posts from all data sources every 15 minutes.

**Sources:**
- Instagram (Apify Instagram Hashtag Scraper / Basic Display API)
- TikTok (Apify TikTok Scraper)
- Pinterest (Pinterest API v5)
- Google Trends (pytrends)

**Process:**
```
1. Fetch posts from source API
2. Deduplicate by URL hash
3. Save to raw_posts table
4. Queue for Agent 2 + Agent 3 processing
5. Update source.last_scraped_at
```

**Fallback:** All scrapers have mock data mode for development without API keys.

---

### Agent 2: Vision Analyzer (`app/ai/vision_model.py`)
**Role:** Classifies fashion images using CLIP zero-shot model.

**Process:**
```
1. Download image from image_url
2. Classify clothing type (CLIP vs 20 clothing labels)
3. Detect pattern (CLIP vs 14 pattern labels)
4. Identify style tags (CLIP vs 16 style labels, threshold 0.05)
5. Extract color palette via K-means (sklearn, 5 clusters)
6. Generate 512-dim CLIP embedding for Pinecone
7. Save ImageFeature record
```

**Models:** `openai/clip-vit-base-patch32` via HuggingFace Transformers  
**Fallback:** Mock classification when PyTorch unavailable (returns hardcoded values)

---

### Agent 3: Trend Analyzer (`app/ai/nlp_model.py`)
**Role:** Extracts trends from text content using NLP.

**Hashtag scoring algorithm:**
```
engagement_weight = min(likes*1 + comments*3 + shares*5 + views*0.1, 1.0)
hashtag_score = (1 + engagement_weight) per occurrence
trend_score = volume_component(40%) + growth_component(40%) + engagement_component(20%)
```

**Process:**
```
1. Extract hashtags from caption (regex)
2. Extract keywords (KeyBERT / TF-IDF fallback)
3. Analyse sentiment (TextBlob / heuristic fallback)
4. Classify topics [Style, Color, Fabric, Season, Occasion]
5. Save TextFeature record
6. Detect emerging trends (lookback 24h, min 3 posts, engagement-weighted)
```

---

### Agent 4: Forecast Agent (`app/ai/forecasting.py`)
**Role:** Predicts trend scores 7–365 days ahead using ML ensemble.

**Models:**

| Model | Fallback | Best for |
|-------|----------|---------|
| **Prophet** | Exponential Triple Smoothing (ETS) | Seasonality patterns, fashion quarters |
| **LSTM** | Auto-Regressive (AR-3) | Sequence momentum, viral spikes |
| **XGBoost** | Linear Regression | Feature-based demand signals |

**Prophet features:**
- Custom `fashion_quarter` seasonality (period=91.25 days, fourier_order=5)
- Weekly + yearly seasonality
- `changepoint_prior_scale=0.1` (conservative)

**LSTM architecture:**
- 2 layers, hidden_size=32
- SEQ_LEN=30 days look-back
- Iterative multi-step forecasting
- Uncertainty from std of last 7 predictions

**XGBoost features:**
- lag1, lag2, lag3 (previous values)
- rolling_mean(7d), rolling_std(7d)
- growth rate
- month, quarter (seasonality encoding)

**Confidence decay:**
```python
confidence = base_conf * exp(-horizon_days / 180)
# 30-day: ~85% of base
# 90-day: ~63% of base
# 180-day: ~37% of base
```

---

### Agent 5: Business Advisor (`app/services/ai_service.py`)
**Role:** Generates personalized inventory recommendations via Claude.

**System prompt context includes:**
- Top 10 current trends with scores, growth, status, region
- User's subscription tier and region

**Recommendation logic:**
```
score ≥ 80 AND growth ≥ 30%  → stock_now    (priority: high)
score ≥ 60 AND growth ≥ 15%  → monitor      (priority: medium)
growth < -10%                 → reduce_inventory (priority: high)
else                          → monitor      (priority: low)
```

**Claude model:** `claude-sonnet-4-20250514`  
**Max tokens:** 500 (advisor chat), 120 (trend descriptions), 80 (recommendation reasoning)

---

## 7. Backend Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 16
- Redis 7
- MongoDB 7 (optional, for raw data lake)

### Quick Start (Local)

```bash
# 1. Clone and enter
cd fashion-trend-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database URL and API keys

# 5. Run database migrations
alembic upgrade head

# 6. Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start Celery worker (new terminal)
celery -A app.workers.scheduler.celery_app worker --loglevel=info

# 8. Start Celery beat scheduler (new terminal)
celery -A app.workers.scheduler.celery_app beat --loglevel=info
```

### Makefile Commands

```bash
make install        # Install all dependencies
make dev            # Start API with hot-reload
make worker         # Start Celery worker
make beat           # Start Celery beat
make flower         # Start Flower monitoring UI (port 5555)
make test           # Run all tests
make test-cov       # Run tests with HTML coverage report
make migrate        # Apply all migrations
make migrate-new    # Create new migration (prompts for message)
make docker-up      # Start all services via Docker Compose
make docker-down    # Stop all Docker services
make scrape         # Manually trigger all scrapers
make seed           # Seed subscription plans
make lint           # Run ruff linter
make format         # Auto-format with black + isort
make clean          # Remove cache files
```

---

## 8. Frontend Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Quick Start

```bash
# 1. Enter frontend directory
cd fashion-frontend

# 2. Configure environment
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Install dependencies
npm install

# 4. Start development server
npm run dev
# → http://localhost:3000

# 5. Build for production
npm run build
npm start
```

---

## 9. Environment Variables

### Backend (`.env`)

```bash
# ── Application ──────────────────────────────────────────────
APP_NAME="Fashion Trend AI"
APP_VERSION="1.0.0"
ENVIRONMENT=development          # development | staging | production
DEBUG=true
SECRET_KEY=your-32-char-minimum-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# ── PostgreSQL ────────────────────────────────────────────────
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=fashion_user
POSTGRES_PASSWORD=fashion_password
POSTGRES_DB=fashion_trend_db
DATABASE_URL=postgresql+asyncpg://fashion_user:fashion_password@localhost:5432/fashion_trend_db
DATABASE_URL_SYNC=postgresql://fashion_user:fashion_password@localhost:5432/fashion_trend_db

# ── Redis ─────────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# ── MongoDB ───────────────────────────────────────────────────
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=fashion_raw_data

# ── AWS S3 ────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=fashion-trend-raw-data

# ── Pinecone (Vector DB) ──────────────────────────────────────
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=fashion-trends

# ── AI Keys ───────────────────────────────────────────────────
ANTHROPIC_API_KEY=your-anthropic-api-key        # Required for AI Advisor
OPENAI_API_KEY=your-openai-api-key              # Optional

# ── Social Media Scraping ─────────────────────────────────────
APIFY_API_TOKEN=your-apify-token                # Primary scraper (recommended)
INSTAGRAM_ACCESS_TOKEN=your-instagram-token     # Optional (Basic Display API)
TIKTOK_CLIENT_KEY=your-tiktok-key              # Optional
TIKTOK_CLIENT_SECRET=your-tiktok-secret        # Optional
PINTEREST_ACCESS_TOKEN=your-pinterest-token    # Optional
YOUTUBE_API_KEY=your-youtube-api-key           # Optional
SERPAPI_KEY=your-serpapi-key                   # For Google Trends alternative

# ── Stripe (Payments) ─────────────────────────────────────────
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
STRIPE_PRICE_BASIC=price_xxxxxxxxxxxxxxxx       # Basic plan Stripe price ID
STRIPE_PRICE_PRO=price_xxxxxxxxxxxxxxxx         # Pro plan Stripe price ID
STRIPE_PRICE_PREMIUM=price_xxxxxxxxxxxxxxxx     # Premium plan Stripe price ID

# ── Email (SendGrid) ──────────────────────────────────────────
SENDGRID_API_KEY=SG.your-sendgrid-api-key
FROM_EMAIL=noreply@fashiontrend.ai

# ── SMS (Twilio) ──────────────────────────────────────────────
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# ── CORS ──────────────────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# ── Rate Limiting ─────────────────────────────────────────────
RATE_LIMIT_PER_MINUTE=60

# ── Scraper Schedule ──────────────────────────────────────────
SCRAPE_INTERVAL_MINUTES=15
TREND_ANALYSIS_INTERVAL_MINUTES=30
FORECAST_INTERVAL_HOURS=6
```

### Frontend (`.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 10. API Reference

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** Bearer token in `Authorization` header  
**Docs:** http://localhost:8000/docs (Swagger UI)

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | None | Create account |
| POST | `/auth/login` | None | Get JWT tokens |
| POST | `/auth/refresh` | None | Refresh access token |
| GET  | `/auth/me` | ✓ | Current user profile |
| POST | `/auth/logout` | ✓ | Logout |

**Register request:**
```json
{
  "name": "Alex Chen",
  "email": "alex@boutique.com",
  "password": "securepass123",
  "role": "boutique_owner"
}
```

**Login response:**
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### Trends

| Method | Endpoint | Auth | Plan | Description |
|--------|----------|------|------|-------------|
| GET | `/trends/` | ✓ | Any | List trends (filtered, sorted, paginated) |
| GET | `/trends/dashboard` | ✓ | Any | Dashboard summary stats |
| GET | `/trends/rising` | ✓ | Any | Currently rising trends |
| GET | `/trends/categories` | ✓ | Any | List all categories |
| GET | `/trends/{id}` | ✓ | Any | Single trend detail |
| POST | `/trends/` | ✓ | Admin | Create trend |
| PATCH | `/trends/{id}` | ✓ | Admin | Update trend |
| DELETE | `/trends/{id}` | ✓ | Admin | Delete trend |

**Trend filters (query params):**
```
category=Style
region=Global
status=rising
min_score=60
date_from=2025-01-01
date_to=2025-04-30
search=quiet+luxury
sort_by=trend_score    (trend_score|growth_rate|date|name)
sort_order=desc        (asc|desc)
page=1
page_size=20
```

---

### Predictions

| Method | Endpoint | Auth | Plan | Description |
|--------|----------|------|------|-------------|
| GET | `/predictions/` | ✓ | Any | List predictions |
| POST | `/predictions/generate` | ✓ | Pro+ | Run ML forecast |
| GET | `/predictions/seasons` | ✓ | Any | Season-level forecasts |
| GET | `/predictions/{id}` | ✓ | Any | Single prediction |

**Generate request:**
```json
{
  "trend_id": "uuid-here",
  "horizon_days": 30,
  "models": ["prophet", "lstm", "xgboost"]
}
```

---

### Recommendations

| Method | Endpoint | Auth | Plan | Description |
|--------|----------|------|------|-------------|
| GET | `/recommendations/` | ✓ | Pro+ | List recommendations |
| PATCH | `/recommendations/{id}` | ✓ | Pro+ | Mark as read |
| POST | `/advisor/recommendations/refresh` | ✓ | Pro+ | Regenerate all |

---

### Alerts

| Method | Endpoint | Auth | Plan | Description |
|--------|----------|------|------|-------------|
| GET | `/alerts/` | ✓ | Any | List my alerts |
| POST | `/alerts/` | ✓ | Any | Create alert rule |
| DELETE | `/alerts/{id}` | ✓ | Any | Delete alert |
| PATCH | `/alerts/{id}/toggle` | ✓ | Any | Toggle active |

**Create alert:**
```json
{
  "trend_id": "uuid-here",
  "alert_type": "trend_spike",
  "threshold": 85.0,
  "channels": ["email", "in_app"]
}
```

---

### Reports

| Method | Endpoint | Auth | Plan | Description |
|--------|----------|------|------|-------------|
| GET | `/reports/` | ✓ | Any | List my reports |
| POST | `/reports/` | ✓ | Pro+ | Generate report (async) |
| GET | `/reports/{id}` | ✓ | Any | Get report status + data |
| DELETE | `/reports/{id}` | ✓ | Any | Delete report |

---

### Subscriptions

| Method | Endpoint | Auth | Plan | Description |
|--------|----------|------|------|-------------|
| GET | `/subscriptions/plans` | None | — | List all plans (public) |
| GET | `/subscriptions/me` | ✓ | Any | My current subscription |
| POST | `/subscriptions/` | ✓ | Any | Subscribe to a plan |
| DELETE | `/subscriptions/me` | ✓ | Any | Cancel subscription |
| POST | `/subscriptions/webhook` | None | — | Stripe webhook |

---

### AI Advisor

| Method | Endpoint | Auth | Plan | Description |
|--------|----------|------|------|-------------|
| POST | `/advisor/chat` | ✓ | Pro+ | Chat with AI advisor |
| GET | `/colors/palette` | ✓ | Any | Current color palette |
| GET | `/colors/rising` | ✓ | Any | Rising colors |
| POST | `/scraper/trigger` | ✓ | Admin | Trigger manual scrape |
| GET | `/scraper/status/{task_id}` | ✓ | Admin | Check scraper task status |

---

## 11. Payment Gateway

### Overview
All payments are processed by **Stripe**. The backend handles the complete payment lifecycle — the frontend never touches card data directly.

### Payment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments/checkout-session` | Create Stripe-hosted checkout page |
| GET  | `/payments/checkout-session/{id}` | Verify payment after redirect |
| POST | `/payments/payment-intent` | Embedded Stripe Elements flow |
| POST | `/payments/upgrade` | Upgrade/downgrade plan with proration |
| POST | `/payments/billing-portal` | Stripe self-service portal |
| GET  | `/payments/invoices` | Invoice history with PDF links |
| GET  | `/payments/payment-methods` | Saved cards |
| DELETE | `/payments/payment-methods/{id}` | Remove a card |
| POST | `/payments/cancel` | Cancel subscription |
| POST | `/payments/reactivate` | Reactivate cancelled subscription |
| POST | `/payments/webhook` | Stripe webhook (15 event types) |

### Payment Flow

```
User → /subscription → selects plan
     → /checkout (CheckoutPage component)
     → POST /payments/checkout-session
     → Stripe-hosted checkout page
     → Card payment on Stripe
     → Redirect to /checkout/success?session_id=cs_xxx
     → GET /payments/checkout-session/cs_xxx (verify)
     → DB updated to status=active
     → Welcome email via SendGrid
     → User redirected to /dashboard
```

### Webhook Events Handled

| Event | Action | Email |
|-------|--------|-------|
| `checkout.session.completed` | Activate subscription | Welcome email |
| `invoice.payment_succeeded` | Set status=active | Payment receipt |
| `invoice.payment_failed` | Set status=past_due | Payment failed notice |
| `customer.subscription.updated` | Sync status | — |
| `customer.subscription.deleted` | Set status=canceled | Cancellation email |
| `customer.subscription.trial_will_end` | — | Trial ending reminder (3 days) |
| `charge.refunded` | — | Refund confirmation |

### Stripe Setup Steps

1. Create products in Stripe Dashboard for Basic/Pro/Premium
2. Add price IDs to `.env`:
   ```bash
   STRIPE_PRICE_BASIC=price_xxxxxxxxxxxxx
   STRIPE_PRICE_PRO=price_xxxxxxxxxxxxx
   STRIPE_PRICE_PREMIUM=price_xxxxxxxxxxxxx
   ```
3. Register webhook endpoint in Stripe Dashboard: `POST https://yourdomain.com/api/v1/payments/webhook`
4. Select webhook events: all `customer.subscription.*`, `invoice.*`, `checkout.session.*`, `charge.refunded`
5. Copy webhook signing secret: `STRIPE_WEBHOOK_SECRET=whsec_xxxxx`

### Trial Periods
- All new subscriptions: **14-day free trial** (configurable)
- No card required during trial
- Trial ending email sent automatically 3 days before expiry
- Subscription activates automatically after trial if card on file

---

## 12. Subscription Plans

| Feature | Basic ($49/mo) | Pro ($149/mo) | Premium ($399/mo) |
|---------|:-:|:-:|:-:|
| Weekly trend reports | ✓ | ✓ | ✓ |
| Top 10 trending colors | ✓ | ✓ | ✓ |
| Basic style explorer | ✓ | ✓ | ✓ |
| Daily trend predictions | — | ✓ | ✓ |
| AI Advisor (Claude chat) | — | ✓ | ✓ |
| Color palette generator | — | ✓ | ✓ |
| Custom PDF/Excel reports | — | ✓ | ✓ |
| Recommendation engine | — | ✓ | ✓ |
| API access | — | ✓ | ✓ |
| Custom alert rules | — | — | ✓ |
| Competitor tracking | — | — | ✓ |
| Real-time AI recommendations | — | — | ✓ |
| White-label reports | — | — | ✓ |
| Max users | 1 | 5 | Unlimited |
| Priority support | — | — | ✓ |
| Yearly pricing | $39/mo | $119/mo | $319/mo |

**Plan enforcement:** The `require_plan("Pro", "Premium")` dependency guard checks active subscription before each protected endpoint. Returns HTTP 402 if plan insufficient.

---

## 13. Background Workers

All background tasks run via **Celery** with Redis as broker. Monitor at http://localhost:5555 (Flower).

| Task | Schedule | Description |
|------|----------|-------------|
| `task_scrape_all_sources` | Every 15 min | Agent 1: Collect raw posts from all sources |
| `task_analyse_trends` | Every 30 min | Agent 3: NLP trend detection from recent posts |
| `task_run_forecasts` | Every 6 hours | Agent 4: ML forecasting for active trends |
| `task_generate_recommendations` | Every 12 hours | Agent 5: Personalized recs for Pro/Premium users |
| `task_check_alerts` | Every 5 min | Evaluate alert rules, trigger notifications |
| `task_daily_cleanup` | 3:00 AM UTC | Remove raw posts >90 days, expired reports |

### Running Workers

```bash
# Worker (processes tasks)
celery -A app.workers.scheduler.celery_app worker --loglevel=info --concurrency=4

# Beat (sends scheduled tasks)
celery -A app.workers.scheduler.celery_app beat --loglevel=info

# Monitor
celery -A app.workers.scheduler.celery_app flower --port=5555
```

### Manual Trigger

```bash
# Trigger scraper via API
curl -X POST http://localhost:8000/api/v1/scraper/trigger \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sources": ["Instagram", "TikTok"], "limit_per_source": 50}'

# Or via Makefile
make scrape
```

---

## 14. Frontend Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | — | Redirects to /dashboard |
| `/login` | `AuthPages.tsx` | Editorial login with social proof stats |
| `/register` | `AuthPages.tsx` | Sign up with role selector (Boutique / Store / Designer) |
| `/dashboard` | `DashboardPage.tsx` | Stats grid, AI agent cards, trend table, area chart, source sparklines |
| `/trends` | `TrendsPage.tsx` | Filterable table + grid view, search, category/region/status filters |
| `/predictions` | `PredictionsPage.tsx` | Season forecasts, 30-day forecast chart, radar chart, model info |
| `/agents` | `OtherPages.tsx` | 5 AI agent detail cards with live stats |
| `/colors` | `OtherPages.tsx` | Interactive color swatch palette, detail panel, rising/declining |
| `/advisor` | `AdvisorPage.tsx` | Claude-powered chat with quick prompts, context panel, copy button |
| `/reports` | `OtherPages.tsx` | Report list with download, generate form |
| `/subscription` | `OtherPages.tsx` | Plan comparison with monthly/yearly toggle |
| `/checkout` | `PaymentPages.tsx` | Plan selector, Stripe Checkout redirect, trial info |
| `/checkout/success` | `PaymentPages.tsx` | Payment confirmation with details |
| `/billing` | `PaymentPages.tsx` | Full billing: invoices, cards, upgrade, cancel, portal |

---

## 15. UI Design System

### Color Palette

```css
--bg:         #0A0A0F   /* Page background */
--surface:    #111118   /* Elevated surfaces (auth cards, nav) */
--card:       #16161F   /* Content cards */
--border:     #1E1E2E   /* Dividers, card borders */
--accent:     #C9A96E   /* Gold — primary brand accent */
--rose:       #D4688A   /* Secondary — alerts, decline */
--teal:       #4ECDC4   /* Tertiary — emerging trends */
--violet:     #7C5CBF   /* Quaternary — predictions */
--jade:       #52C97A   /* Success — rising trends */
--text:       #F0EEE8   /* Primary text */
--muted:      #6B6B7A   /* Secondary text, labels */
```

### Typography

```css
--font-serif: 'Cormorant Garamond', Georgia, serif  /* Display headings */
--font-sans:  'DM Sans', system-ui, sans-serif      /* Body text, UI */
--font-mono:  'DM Mono', monospace                  /* Code, hex colors */
```

### Status Badge Classes

```css
.badge-rising    /* Green  — growing trend */
.badge-peak      /* Gold   — at maximum */
.badge-emerging  /* Teal   — new signal */
.badge-declining /* Rose   — fading */
.badge-stable    /* Gray   — steady state */
```

### UI Components (`src/components/ui/index.tsx`)

- `Button` — primary / ghost / danger / outline variants, loading spinner
- `Input` — with label, error, hint states
- `Select` — styled dropdown with label
- `Card` — with optional hover animation and accent color top border
- `CardHeader / CardTitle / CardBody` — card sections
- `Badge` — auto-colors from status string
- `StatCard` — big number with label, change, color bar
- `ScoreBar` — horizontal progress bar with score label
- `Sparkline` — mini bar chart from data array
- `Spinner` — animated loading indicator
- `Empty` — empty state with icon, title, description, action
- `Skeleton / SkeletonCard` — shimmer loading placeholder
- `SectionHeader` — page title with subtitle and action slot
- `Tag` — colored label pill
- `ColorDot` — colored circle with glow
- `Progress` — thin confidence bar

---

## 16. Docker Deployment

### Services

```yaml
postgres     # PostgreSQL 16 — port 5432
redis        # Redis 7       — port 6379
mongodb      # MongoDB 7     — port 27017
api          # FastAPI       — port 8000
celery_worker # Celery worker
celery_beat  # Celery scheduler
flower       # Task monitor  — port 5555
```

### Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Run migrations
docker-compose exec api alembic upgrade head

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose build --no-cache api
docker-compose up -d api

# Full rebuild
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

### Access Points After docker-compose up

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| Flower Monitor | http://localhost:5555 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| MongoDB | localhost:27017 |

---

## 17. Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Specific file
pytest tests/api/test_payments.py -v

# Skip slow tests
pytest tests/ -m "not slow and not integration"
```

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_auth.py` | 12 | Auth register, login, refresh, JWT, me |
| `test_trends.py` | 16 | CRUD, filters, sorting, pagination, dashboard |
| `test_endpoints.py` | 18 | Subscriptions, alerts, reports, users, recommendations |
| `test_payments.py` | 31 | Full payment gateway + 8 webhook event types |
| `test_ai_agents.py` | 40 | NLP, Vision, Prophet, LSTM, XGBoost, helpers |
| `test_scraper.py` | 12 | All 4 scrapers, orchestrator, mock data |
| **Total** | **129** | |

### Test Architecture

Tests use **SQLite in-memory** database (no PostgreSQL needed) via `aiosqlite`. All Stripe SDK calls are mocked with `unittest.mock.patch`. The `conftest.py` provides:
- `basic_user` — boutique owner with no subscription
- `pro_user` — user with active Pro subscription
- `admin_user` — admin role
- `basic_token / pro_token / admin_token` — pre-generated JWT tokens
- `client` — AsyncClient (httpx) for API requests
- `db_session` — isolated async SQLite session

---

## 18. Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123def

# View migration history
alembic history --verbose

# View current state
alembic current

# Create new migration (auto-detects model changes)
alembic revision --autogenerate -m "add user preference table"

# Create empty migration (manual SQL)
alembic revision -m "add index on trends name"
```

### First-Time Setup

```bash
# Creates all tables from scratch (dev only)
# Production should always use Alembic
python -c "import asyncio; from app.db.base import init_db; asyncio.run(init_db())"

# Or with Alembic (recommended)
alembic upgrade head
```

---

## 19. Required API Keys

### Minimum for Local Dev (no keys needed)
All scrapers have mock data fallbacks. AI Advisor requires ANTHROPIC_API_KEY.

### Recommended Setup

| Key | Service | Required | Get it at |
|-----|---------|----------|-----------|
| `ANTHROPIC_API_KEY` | Claude AI Advisor | **Yes** | platform.anthropic.com |
| `DATABASE_URL` | PostgreSQL | **Yes** | Local or cloud DB |
| `REDIS_URL` | Redis | **Yes** | Local or Upstash |
| `STRIPE_SECRET_KEY` | Payments | **Yes** | dashboard.stripe.com |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhooks | **Yes** | dashboard.stripe.com |
| `STRIPE_PRICE_BASIC` | Basic plan price | **Yes** | Stripe Dashboard |
| `STRIPE_PRICE_PRO` | Pro plan price | **Yes** | Stripe Dashboard |
| `STRIPE_PRICE_PREMIUM` | Premium plan price | **Yes** | Stripe Dashboard |
| `APIFY_API_TOKEN` | Social scraping | Recommended | apify.com |
| `SENDGRID_API_KEY` | Transactional email | Recommended | sendgrid.com |
| `PINECONE_API_KEY` | Vector search | Optional | pinecone.io |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram API | Optional | developers.facebook.com |
| `PINTEREST_ACCESS_TOKEN` | Pinterest API | Optional | developers.pinterest.com |
| `YOUTUBE_API_KEY` | YouTube API | Optional | console.cloud.google.com |
| `AWS_ACCESS_KEY_ID` | S3 file storage | Optional | aws.amazon.com |
| `TWILIO_ACCOUNT_SID` | SMS alerts | Optional | twilio.com |

---

## 20. Production Deployment

### Recommended Stack
- **Backend:** Railway / Render / AWS ECS
- **Frontend:** Vercel
- **Database:** Supabase / AWS RDS (PostgreSQL)
- **Redis:** Upstash / AWS ElastiCache
- **Storage:** AWS S3
- **CDN:** CloudFront

### Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd fashion-frontend
vercel --prod

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL
# Enter: https://your-api-domain.com
```

### Railway (Backend)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and link
railway login
railway link

# Set all env vars
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set DATABASE_URL=postgresql://...
# (repeat for all env vars)

# Deploy
railway up
```

### Production Checklist

```
☐ Set ENVIRONMENT=production in .env
☐ Set DEBUG=false
☐ Generate strong SECRET_KEY (32+ chars)
☐ Configure PostgreSQL with SSL
☐ Use managed Redis (Upstash) instead of local
☐ Set up Stripe webhook endpoint
☐ Verify all STRIPE_PRICE_* IDs are production (not test)
☐ Configure SendGrid verified sender domain
☐ Set ALLOWED_ORIGINS to your frontend domain
☐ Enable HTTPS on all endpoints
☐ Set up CloudWatch/Grafana monitoring
☐ Configure log retention (Loguru rotating files)
☐ Set up database backups
☐ Run alembic upgrade head before first start
☐ Test payment flow end-to-end with Stripe test mode first
☐ Switch Stripe to live mode when ready
```

### Security Notes
- JWT tokens expire in 60 minutes (configurable)
- Refresh tokens expire in 30 days
- All passwords hashed with bcrypt (rounds=12)
- Rate limiting: 60 requests/minute per IP (slowapi)
- Stripe webhook signature verified on every request
- CORS restricted to ALLOWED_ORIGINS
- Non-root Docker user in production image
- SQL injection protection via SQLAlchemy ORM

---

## Quick Reference Card

```bash
# ── Start Everything ──────────────────────────────────────
docker-compose up -d               # All services
docker-compose exec api alembic upgrade head  # Migrations

# ── API ───────────────────────────────────────────────────
http://localhost:8000/docs         # Swagger UI
http://localhost:8000/health       # Health check
http://localhost:5555              # Celery Flower

# ── Frontend ──────────────────────────────────────────────
http://localhost:3000              # App
http://localhost:3000/dashboard    # Main dashboard
http://localhost:3000/checkout     # Start subscription

# ── Common Commands ───────────────────────────────────────
make test                          # Run all 129 tests
make scrape                        # Trigger manual scrape
make migrate-new                   # New DB migration
make docker-up                     # Start Docker stack
make flower                        # Celery monitor

# ── Demo Login ────────────────────────────────────────────
Email:    pro@test.com
Password: password123
```
