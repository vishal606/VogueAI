"""
Pydantic v2 schemas for request/response validation.
"""
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, EmailStr, Field, field_validator
import uuid


# ── Base ──────────────────────────────────────────────────────────────────────

class UUIDMixin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="boutique_owner")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        allowed = {"boutique_owner", "fashion_designer", "online_store"}
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Users ─────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None


class UserResponse(UserBase, TimestampMixin):
    id: str
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


# ── Subscription Plans ────────────────────────────────────────────────────────

class PlanResponse(BaseModel):
    id: str
    name: str
    type: str
    price: float
    features: Dict[str, Any]
    is_active: bool

    model_config = {"from_attributes": True}


# ── Subscriptions ─────────────────────────────────────────────────────────────

class SubscriptionCreate(BaseModel):
    plan_id: str
    payment_method_id: Optional[str] = None  # Stripe payment method


class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    status: str
    start_date: date
    end_date: Optional[date] = None
    plan: Optional[PlanResponse] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Trends ────────────────────────────────────────────────────────────────────

class TrendBase(BaseModel):
    name: str
    category: str
    region: str = "Global"


class TrendCreate(TrendBase):
    trend_score: float = 0.0
    growth_rate: float = 0.0
    status: str = "emerging"
    date: date = Field(default_factory=date.today)
    color_hex: Optional[str] = None
    top_hashtags: Optional[List[str]] = None


class TrendUpdate(BaseModel):
    trend_score: Optional[float] = None
    growth_rate: Optional[float] = None
    status: Optional[str] = None
    source_breakdown: Optional[Dict[str, Any]] = None


class TrendResponse(TrendBase, TimestampMixin):
    id: str
    trend_score: float
    growth_rate: float
    status: str
    date: date
    color_hex: Optional[str] = None
    top_hashtags: Optional[List[str]] = None
    source_breakdown: Dict[str, Any] = {}

    model_config = {"from_attributes": True}


class TrendListResponse(BaseModel):
    trends: List[TrendResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class TrendFilter(BaseModel):
    category: Optional[str] = None
    region: Optional[str] = None
    status: Optional[str] = None
    min_score: Optional[float] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    search: Optional[str] = None


# ── Predictions ───────────────────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    id: str
    trend_id: str
    predicted_value: float
    prediction_date: date
    confidence: float
    model_used: str
    horizon_days: int
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    season: Optional[str] = None
    factors: Dict[str, Any] = {}
    trend: Optional[TrendResponse] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PredictionRequest(BaseModel):
    trend_id: str
    horizon_days: int = Field(default=30, ge=7, le=365)
    models: List[str] = Field(default=["prophet", "lstm", "xgboost"])


class SeasonForecastResponse(BaseModel):
    season: str
    trend_name: str
    confidence: float
    description: str
    predicted_score: float
    key_factors: List[str]


# ── Recommendations ───────────────────────────────────────────────────────────

class RecommendationResponse(BaseModel):
    id: str
    user_id: str
    trend_id: str
    action: str
    description: str
    priority: str
    confidence_score: float
    is_read: bool
    ai_reasoning: Optional[str] = None
    trend: Optional[TrendResponse] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RecommendationUpdate(BaseModel):
    is_read: bool


# ── Alerts ────────────────────────────────────────────────────────────────────

class AlertCreate(BaseModel):
    trend_id: Optional[str] = None
    alert_type: str  # trend_spike | trend_decline | new_trend | recommendation
    threshold: Optional[float] = None
    channels: List[str] = Field(default=["email"])  # email | sms | push

    @field_validator("channels")
    @classmethod
    def validate_channels(cls, v):
        allowed = {"email", "sms", "push", "in_app"}
        for c in v:
            if c not in allowed:
                raise ValueError(f"Channel must be one of: {allowed}")
        return v


class AlertResponse(BaseModel):
    id: str
    user_id: str
    trend_id: Optional[str] = None
    alert_type: str
    threshold: Optional[float] = None
    triggered: bool
    triggered_at: Optional[datetime] = None
    channels: List[str]
    message: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Reports ───────────────────────────────────────────────────────────────────

class ReportCreate(BaseModel):
    title: str
    report_type: str  # weekly_trends | color_palette | season_forecast | recommendations | custom
    filters: Dict[str, Any] = {}


class ReportResponse(BaseModel):
    id: str
    user_id: str
    title: str
    report_type: str
    file_url: Optional[str] = None
    status: str
    filters: Dict[str, Any] = {}
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Sources ───────────────────────────────────────────────────────────────────

class SourceResponse(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None
    is_active: bool
    last_scraped_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Scraper ───────────────────────────────────────────────────────────────────

class ScraperTriggerRequest(BaseModel):
    sources: Optional[List[str]] = None  # None = all sources
    limit_per_source: int = Field(default=100, ge=10, le=1000)


class ScraperStatusResponse(BaseModel):
    task_id: str
    status: str
    sources: List[str]
    started_at: datetime
    message: str


# ── AI Advisor ────────────────────────────────────────────────────────────────

class AdvisorMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    context: Optional[Dict[str, Any]] = None  # Optional context: user's region, category focus, etc.


class AdvisorMessageResponse(BaseModel):
    response: str
    sources_used: List[str] = []
    related_trends: List[str] = []
    suggested_actions: List[str] = []


# ── Color Trends ─────────────────────────────────────────────────────────────

class ColorTrendResponse(BaseModel):
    color_name: str
    hex_code: str
    percentage: float
    growth_rate: float
    trend_status: str
    category_breakdown: Dict[str, float]
    top_brands: List[str]


class ColorPaletteResponse(BaseModel):
    season: str
    colors: List[ColorTrendResponse]
    generated_at: datetime


# ── Dashboard Summary ─────────────────────────────────────────────────────────

class DashboardSummaryResponse(BaseModel):
    total_trends_tracked: int
    data_points_today: int
    prediction_accuracy: float
    active_brands: int
    top_trends: List[TrendResponse]
    agent_status: Dict[str, str]
    last_updated: datetime


# ── Stripe Webhook ────────────────────────────────────────────────────────────

class StripeWebhookPayload(BaseModel):
    type: str
    data: Dict[str, Any]


# ── Pagination ────────────────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
