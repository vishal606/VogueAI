from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────────
    APP_NAME: str = "Fashion Trend AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ── Security ─────────────────────────────────────────────
    SECRET_KEY: str = "changeme-in-production-use-32-char-minimum"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./fashion_trend.db"
    DATABASE_URL_SYNC: str = "sqlite:///./fashion_trend.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # ── Legacy PostgreSQL fields (for backward compatibility) ──
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "fashion_user"
    POSTGRES_PASSWORD: str = "fashion_password"
    POSTGRES_DB: str = "fashion_trend_db"

    # ── Redis ────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── MongoDB ──────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "fashion_raw_data"

    # ── AWS S3 ───────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "fashion-trend-raw-data"

    # ── Pinecone ─────────────────────────────────────────────
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-east-1-aws"
    PINECONE_INDEX_NAME: str = "fashion-trends"

    # ── AI ───────────────────────────────────────────────────
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # ── Social Media APIs ────────────────────────────────────
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    PINTEREST_ACCESS_TOKEN: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None

    # ── E-Commerce ───────────────────────────────────────────
    RAPIDAPI_KEY: Optional[str] = None
    APIFY_API_TOKEN: Optional[str] = None
    SERPAPI_KEY: Optional[str] = None

    # ── Google ───────────────────────────────────────────────
    GOOGLE_TRENDS_GEO: str = "US"

    # ── Stripe ───────────────────────────────────────────────
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_BASIC: str = "price_basic_monthly"
    STRIPE_PRICE_PRO: str = "price_pro_monthly"
    STRIPE_PRICE_PREMIUM: str = "price_premium_monthly"

    # ── Email ────────────────────────────────────────────────
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@fashiontrend.ai"

    # ── Twilio ───────────────────────────────────────────────
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # ── CORS ─────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # ── Rate Limits ──────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_DAY: int = 1000

    # ── Scraper Schedule ─────────────────────────────────────
    SCRAPE_INTERVAL_MINUTES: int = 15
    TREND_ANALYSIS_INTERVAL_MINUTES: int = 30
    FORECAST_INTERVAL_HOURS: int = 6

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
