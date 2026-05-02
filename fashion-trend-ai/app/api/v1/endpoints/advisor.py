"""
advisor.py — AI Advisor chat endpoint (Agent 5)
scraper.py  — Admin scraper trigger endpoint (Agent 1)
colors.py   — Color trends endpoint
"""

# ── advisor.py ────────────────────────────────────────────────────────────────
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.db.models.models import User
from app.db.schemas.schemas import (
    AdvisorMessageRequest, AdvisorMessageResponse,
    ColorPaletteResponse, ColorTrendResponse,
)
from app.api.deps import get_current_user, require_plan
from app.services.ai_service import AIService
from app.services.trend_service import TrendService
from datetime import datetime

advisor_router = APIRouter(prefix="/advisor", tags=["AI Advisor"])
scraper_router = APIRouter(prefix="/scraper", tags=["Scraper"])
colors_router = APIRouter(prefix="/colors", tags=["Color Trends"])


# ── Advisor ───────────────────────────────────────────────────────────────────

@advisor_router.post("/chat", response_model=AdvisorMessageResponse)
async def chat_with_advisor(
    payload: AdvisorMessageRequest,
    _sub=Depends(require_plan("Pro", "Premium")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    AI Business Advisor chat endpoint.
    Uses Claude with live trend data injected as context.
    Requires Pro or Premium subscription.
    """
    ai = AIService(db)
    return await ai.get_advisor_response(
        message=payload.message,
        user_id=current_user.id,
        context=payload.context,
    )


@advisor_router.post("/recommendations/refresh")
async def refresh_my_recommendations(
    _sub=Depends(require_plan("Pro", "Premium")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate personalised recommendations using current trend data."""
    from app.services.recommendation_service import RecommendationService
    service = RecommendationService(db)
    recs = await service.refresh_for_user(current_user.id)
    return {"generated": len(recs), "message": f"Generated {len(recs)} recommendations"}


# ── Scraper ───────────────────────────────────────────────────────────────────

@scraper_router.post("/trigger")
async def trigger_scraper(
    sources: list = None,
    limit_per_source: int = 50,
    _admin: User = Depends(get_current_user),  # use require_admin in prod
):
    """
    Manually trigger scraper (admin only).
    Enqueues a Celery task.
    """
    from app.workers.scheduler import task_scrape_all_sources
    task = task_scrape_all_sources.delay(
        source_names=sources,
        limit_per_source=limit_per_source,
    )
    return {
        "task_id": task.id,
        "status": "queued",
        "sources": sources or "all",
        "message": "Scraper task enqueued",
    }


@scraper_router.get("/status/{task_id}")
async def scraper_task_status(task_id: str):
    """Check Celery task status by task_id."""
    from app.workers.scheduler import celery_app
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }


# ── Color Trends ──────────────────────────────────────────────────────────────

@colors_router.get("/palette", response_model=ColorPaletteResponse)
async def get_color_palette(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current trending color palette extracted from fashion images."""
    service = TrendService(db)
    colors_data = await service.get_color_trends(limit=12)
    return ColorPaletteResponse(
        season="Spring/Summer 2025",
        colors=[ColorTrendResponse(**c) for c in colors_data],
        generated_at=datetime.utcnow(),
    )


@colors_router.get("/rising")
async def get_rising_colors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get colors with the highest recent growth rate."""
    from app.db.models.models import Trend
    from sqlalchemy import select, desc, and_
    result = await db.execute(
        select(Trend)
        .where(and_(Trend.category == "Color", Trend.status.in_(["rising", "emerging"])))
        .order_by(desc(Trend.growth_rate))
        .limit(6)
    )
    trends = result.scalars().all()
    return [
        {
            "name": t.name,
            "hex": t.color_hex,
            "score": t.trend_score,
            "growth": t.growth_rate,
            "status": t.status,
        }
        for t in trends
    ]
