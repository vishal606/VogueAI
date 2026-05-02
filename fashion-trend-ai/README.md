# 🧵 Fashion Trend AI — Backend

> **AI-Powered Fashion Trend Prediction Platform**  
> Multi-agent FastAPI backend collecting, analyzing and forecasting fashion trends  
> from social media and e-commerce for boutique owners and fashion stores.

---

## 🏗️ Architecture Overview

```
fashion-trend-ai/
├── app/
│   ├── main.py                    # FastAPI app factory + lifespan
│   ├── core/
│   │   ├── config.py              # Pydantic Settings (env vars)
│   │   └── security.py            # JWT auth, password hashing
│   ├── db/
│   │   ├── base.py                # SQLAlchemy async engine + session
│   │   ├── models/models.py       # All ORM models (matches ER diagram)
│   │   └── schemas/schemas.py     # Pydantic v2 request/response schemas
│   ├── api/
│   │   ├── deps.py                # Auth deps, subscription guards, pagination
│   │   └── v1/
│   │       ├── router.py          # Assembles all endpoint routers
│   │       └── endpoints/
│   │           ├── auth.py        # Register, login, refresh, /me
│   │           ├── users.py       # User profile CRUD
│   │           ├── trends.py      # Trend listing, filtering, dashboard
│   │           ├── predictions.py # Forecast generation + season forecasts
│   │           ├── recommendations.py  # AI business recommendations
│   │           ├── alerts.py      # Custom alert rules
│   │           ├── reports.py     # Report generation + download
│   │           ├── subscriptions.py    # Stripe billing + webhook
│   │           └── advisor.py     # AI chat, color trends, scraper trigger
│   ├── services/
│   │   ├── trend_service.py       # Dashboard, scoring, report generation
│   │   ├── ai_service.py          # Agent orchestration + Claude advisor
│   │   └── recommendation_service.py  # Recommendation lifecycle
│   ├── ai/
│   │   ├── vision_model.py        # Agent 2: CLIP image classification
│   │   ├── nlp_model.py           # Agent 3: NLP, hashtags, sentiment
│   │   └── forecasting.py         # Agent 4: Prophet + LSTM + XGBoost
│   ├── workers/
│   │   ├── scraper.py             # Agent 1: Multi-source scraper
│   │   └── scheduler.py           # Celery tasks + beat schedule
│   └── utils/
│       ├── logger.py              # Loguru logger setup
│       └── helpers.py             # Color math, formatting, utils
├── alembic/                       # DB migrations
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🤖 The 5 AI Agents

| Agent | Role | Technology |
|-------|------|------------|
| **Agent 1**: Trend Collector | Scrapes Instagram, TikTok, Pinterest, Google Trends every 15 min | httpx + Apify |
| **Agent 2**: Vision Analyzer | Classifies clothing type, extracts colors and patterns from images | CLIP (ViT) |
| **Agent 3**: Trend Analyzer | Hashtag analysis, keyword extraction, sentiment scoring | KeyBERT + TextBlob |
| **Agent 4**: Forecast Agent | Predicts trend trajectories 30–90 days ahead | Prophet + LSTM + XGBoost |
| **Agent 5**: Business Advisor | Generates personalized inventory recommendations | Claude (Anthropic) |

---

## 🚀 Quick Start

### 1. Clone & Configure

```bash
git clone <your-repo>
cd fashion-trend-ai
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start with Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **MongoDB** on port 27017
- **FastAPI** on port 8000
- **Celery Worker** (background tasks)
- **Celery Beat** (scheduler)
- **Flower** (task monitor) on port 5555

### 3. Run Migrations

```bash
docker-compose exec api alembic upgrade head
```

### 4. Manual Local Setup (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start services (PostgreSQL, Redis, MongoDB must be running)

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload --port 8000

# Start Celery worker (new terminal)
celery -A app.workers.scheduler.celery_app worker --loglevel=info

# Start Celery beat scheduler (new terminal)
celery -A app.workers.scheduler.celery_app beat --loglevel=info
```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login → get JWT tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET  | `/api/v1/auth/me` | Get current user |

### Trends
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/v1/trends/` | List trends (with filters) |
| GET  | `/api/v1/trends/dashboard` | Dashboard summary stats |
| GET  | `/api/v1/trends/rising` | Currently rising trends |
| GET  | `/api/v1/trends/{id}` | Single trend detail |

### Predictions (Pro+)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/v1/predictions/` | List predictions |
| POST | `/api/v1/predictions/generate` | Run forecast ensemble |
| GET  | `/api/v1/predictions/seasons` | Season-level forecasts |

### AI Advisor (Pro+)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/advisor/chat` | Chat with AI business advisor |
| POST | `/api/v1/advisor/recommendations/refresh` | Regenerate recommendations |

### Subscriptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/v1/subscriptions/plans` | List all plans (public) |
| POST | `/api/v1/subscriptions/` | Subscribe (Stripe) |
| GET  | `/api/v1/subscriptions/me` | Current subscription |
| DELETE | `/api/v1/subscriptions/me` | Cancel subscription |

### Other
```
GET    /api/v1/colors/palette         Color trend palette
GET    /api/v1/colors/rising          Rising colors
GET    /api/v1/alerts/                My alert rules
POST   /api/v1/alerts/                Create alert
GET    /api/v1/reports/               My reports
POST   /api/v1/reports/               Generate report
POST   /api/v1/scraper/trigger        Trigger scraper (admin)
```

---

## 🔑 Required API Keys

| Service | Purpose | Get it at |
|---------|---------|-----------|
| `ANTHROPIC_API_KEY` | AI Advisor (Claude) | platform.anthropic.com |
| `APIFY_API_TOKEN` | Instagram + TikTok scraping | apify.com |
| `STRIPE_SECRET_KEY` | Subscription billing | dashboard.stripe.com |
| `SENDGRID_API_KEY` | Email notifications | sendgrid.com |
| `PINECONE_API_KEY` | Vector similarity search | pinecone.io |

Social media API keys (optional — Apify covers most use cases):
- `INSTAGRAM_ACCESS_TOKEN`
- `PINTEREST_ACCESS_TOKEN`
- `YOUTUBE_API_KEY`

---

## 🔒 Subscription Plan Feature Matrix

| Feature | Basic ($49) | Pro ($149) | Premium ($399) |
|---------|------------|------------|----------------|
| Weekly Trends | ✅ | ✅ | ✅ |
| Color Trends | ✅ | ✅ | ✅ |
| Basic Reports | ✅ | ✅ | ✅ |
| AI Predictions | ❌ | ✅ | ✅ |
| AI Advisor Chat | ❌ | ✅ | ✅ |
| Custom Reports | ❌ | ✅ | ✅ |
| Custom Alerts | ❌ | ❌ | ✅ |
| Competitor Tracking | ❌ | ❌ | ✅ |
| API Access | ❌ | ✅ | ✅ |
| Max Users | 1 | 5 | Unlimited |

---

## ⚙️ Celery Background Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `task_scrape_all_sources` | Every 15 min | Agent 1: Collect raw posts |
| `task_analyse_trends` | Every 30 min | Agent 3: NLP trend detection |
| `task_run_forecasts` | Every 6 hours | Agent 4: ML forecasting |
| `task_generate_recommendations` | Every 12 hours | Agent 5: User recommendations |
| `task_check_alerts` | Every 5 min | Trigger user alert rules |
| `task_daily_cleanup` | 3 AM UTC | Remove stale data |

Monitor tasks at: http://localhost:5555 (Flower UI)

---

## 🧪 Testing

```bash
# Install test deps
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📦 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one
alembic downgrade -1

# View history
alembic history
```

---

## 🌍 Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Use a managed PostgreSQL (e.g. AWS RDS, Supabase)
3. Use a managed Redis (e.g. AWS ElastiCache, Upstash)
4. Deploy with Kubernetes (see `/k8s/` folder — coming soon)
5. Set up CloudFront CDN for report file delivery from S3
6. Configure Stripe webhook endpoint: `POST /api/v1/subscriptions/webhook`

---

## 📖 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

---

## 💳 Payment Gateway (Stripe)

### Backend Endpoints — `/api/v1/payments/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments/checkout-session` | Create Stripe Checkout Session (hosted page) |
| GET  | `/payments/checkout-session/{id}` | Verify payment after redirect |
| POST | `/payments/payment-intent` | Embedded Stripe Elements flow |
| POST | `/payments/upgrade` | Upgrade/downgrade plan with proration |
| POST | `/payments/billing-portal` | Stripe self-service billing portal |
| GET  | `/payments/invoices` | Invoice history |
| GET  | `/payments/payment-methods` | Saved payment methods |
| DELETE | `/payments/payment-methods/{id}` | Remove payment method |
| POST | `/payments/cancel` | Cancel subscription |
| POST | `/payments/reactivate` | Reactivate canceled subscription |
| POST | `/payments/webhook` | Stripe webhook (15 event types) |

### Webhook Events Handled
```
checkout.session.completed          → activate subscription + welcome email
invoice.payment_succeeded           → set active + send receipt email
invoice.payment_failed              → set past_due + send failed email
customer.subscription.updated       → sync status
customer.subscription.deleted       → set canceled + send cancellation email
customer.subscription.trial_will_end → send trial ending reminder email
charge.refunded                     → send refund confirmation email
```

### Frontend Pages
| Route | Description |
|-------|-------------|
| `/subscription` | Plan comparison with pricing toggle |
| `/checkout` | Checkout flow with Stripe redirect |
| `/checkout/success` | Payment confirmation page |
| `/billing` | Full billing management (invoices, cards, upgrade) |

### Stripe Setup
1. Create products in Stripe dashboard for each plan
2. Add price IDs to `.env`:
   ```
   STRIPE_PRICE_BASIC=price_xxxxx
   STRIPE_PRICE_PRO=price_xxxxx
   STRIPE_PRICE_PREMIUM=price_xxxxx
   ```
3. Set up webhook endpoint: `POST /api/v1/payments/webhook`
4. Add webhook secret: `STRIPE_WEBHOOK_SECRET=whsec_xxxxx`
5. Enable events: all subscription, invoice, checkout, charge events

### Trial Period
- All new subscriptions get **14-day free trial** by default
- Trial ending email sent 3 days before expiry
- No card required during trial (configurable)
