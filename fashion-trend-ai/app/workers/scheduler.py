"""
Celery worker + APScheduler for all background tasks:
  - Scrape social media & e-commerce (every 15 min)
  - Run NLP trend analysis (every 30 min)
  - Run forecast models (every 6 hours)
  - Generate user recommendations (every 12 hours)
  - Clean up stale data (daily)
"""
import asyncio
from datetime import datetime
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

from app.core.config import settings

logger = get_task_logger(__name__)

# ── Celery App ────────────────────────────────────────────────────────────────

celery_app = Celery(
    "fashion_trend_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.scheduler"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Retry policy
    task_max_retries=3,
    task_default_retry_delay=60,
)

# ── Beat Schedule ─────────────────────────────────────────────────────────────

celery_app.conf.beat_schedule = {
    # Agent 1: Scrape all sources
    "scrape-all-sources": {
        "task": "app.workers.scheduler.task_scrape_all_sources",
        "schedule": settings.SCRAPE_INTERVAL_MINUTES * 60,  # seconds
        "options": {"expires": settings.SCRAPE_INTERVAL_MINUTES * 60 - 30},
    },

    # Agent 3: Analyse trends from raw posts
    "analyse-trends": {
        "task": "app.workers.scheduler.task_analyse_trends",
        "schedule": settings.TREND_ANALYSIS_INTERVAL_MINUTES * 60,
        "options": {"expires": settings.TREND_ANALYSIS_INTERVAL_MINUTES * 60 - 30},
    },

    # Agent 4: Run forecast ensemble
    "run-forecasts": {
        "task": "app.workers.scheduler.task_run_forecasts",
        "schedule": settings.FORECAST_INTERVAL_HOURS * 3600,
        "options": {"expires": settings.FORECAST_INTERVAL_HOURS * 3600 - 60},
    },

    # Agent 5: Generate recommendations for all active users
    "generate-recommendations": {
        "task": "app.workers.scheduler.task_generate_recommendations",
        "schedule": crontab(hour="*/12"),  # every 12 hours
    },

    # Alert checker
    "check-alerts": {
        "task": "app.workers.scheduler.task_check_alerts",
        "schedule": 300,  # every 5 minutes
    },

    # Daily cleanup
    "daily-cleanup": {
        "task": "app.workers.scheduler.task_daily_cleanup",
        "schedule": crontab(hour=3, minute=0),  # 3 AM UTC daily
    },
}


# ── Helper: run async in sync Celery task ────────────────────────────────────

def run_async(coro):
    """Run an async coroutine from a synchronous Celery task."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ── Task: Scrape Sources ──────────────────────────────────────────────────────

@celery_app.task(name="app.workers.scheduler.task_scrape_all_sources", bind=True, max_retries=3)
def task_scrape_all_sources(self, source_names=None, limit_per_source=100):
    """Agent 1: Collect raw posts from all sources."""
    try:
        from app.workers.scraper import run_scraper_job
        results = run_async(run_scraper_job(
            source_names=source_names,
            limit_per_source=limit_per_source,
        ))
        logger.info(f"[Scraper Task] Results: {results}")
        return results
    except Exception as exc:
        logger.error(f"[Scraper Task] Failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


# ── Task: Analyse Trends ──────────────────────────────────────────────────────

@celery_app.task(name="app.workers.scheduler.task_analyse_trends", bind=True, max_retries=3)
def task_analyse_trends(self):
    """
    Agent 3: Detect emerging trends from recent raw posts.
    Creates/updates Trend records in the DB.
    """
    async def _run():
        from app.db.base import AsyncSessionLocal
        from app.ai.nlp_model import get_nlp_analyzer
        from app.db.models.models import Trend
        from app.services.trend_service import TrendService
        from sqlalchemy import select
        from datetime import date

        nlp = get_nlp_analyzer()
        async with AsyncSessionLocal() as db:
            candidates = await nlp.detect_emerging_trends(db, lookback_hours=24)
            created = 0
            for candidate in candidates[:20]:  # top 20 per cycle
                tag = candidate["hashtag"]
                # Check if trend already exists
                existing = await db.execute(
                    select(Trend).where(Trend.name.ilike(f"%{tag}%")).limit(1)
                )
                if existing.scalar_one_or_none():
                    continue  # Already tracked

                # Compute score
                score, growth = nlp.compute_hashtag_trend_score(
                    current_count=candidate["post_count"],
                    previous_count=max(candidate["post_count"] - 5, 0),
                    engagement_weight=candidate["avg_engagement_weight"],
                )
                service = TrendService(db)
                status = service.classify_status(score, growth)

                trend = Trend(
                    name=tag.replace("_", " ").title(),
                    category="Style",  # refined by vision agent later
                    trend_score=score,
                    growth_rate=growth,
                    status=status,
                    region="Global",
                    date=date.today(),
                    top_hashtags=[tag],
                    source_breakdown={"instagram": {"normalized_score": candidate["avg_engagement_weight"]}},
                )
                db.add(trend)
                created += 1

            await db.commit()
            logger.info(f"[TrendAnalyzer Task] Created {created} new trends")
            return created

    return run_async(_run())


# ── Task: Run Forecasts ───────────────────────────────────────────────────────

@celery_app.task(name="app.workers.scheduler.task_run_forecasts", bind=True, max_retries=2)
def task_run_forecasts(self):
    """Agent 4: Run forecast ensemble on all active rising/peak trends."""
    async def _run():
        from app.db.base import AsyncSessionLocal
        from app.db.models.models import Trend
        from app.services.ai_service import AIService
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Trend)
                .where(Trend.status.in_(["rising", "peak", "emerging"]))
                .limit(20)
            )
            trends = result.scalars().all()
            ai = AIService(db)
            count = 0
            for trend in trends:
                try:
                    await ai.run_forecast_ensemble(
                        trend_id=trend.id,
                        horizon_days=30,
                        models=["prophet", "xgboost"],  # skip LSTM for scheduler speed
                    )
                    count += 1
                except Exception as e:
                    logger.warning(f"[ForecastTask] Failed for {trend.name}: {e}")
            await db.commit()
            logger.info(f"[ForecastTask] Forecasted {count} trends")
            return count

    return run_async(_run())


# ── Task: Generate Recommendations ───────────────────────────────────────────

@celery_app.task(name="app.workers.scheduler.task_generate_recommendations", bind=True)
def task_generate_recommendations(self):
    """Agent 5: Create personalised recommendations for all active Pro/Premium users."""
    async def _run():
        from app.db.base import AsyncSessionLocal
        from app.db.models.models import User, Subscription, SubscriptionPlan
        from app.services.recommendation_service import RecommendationService
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            # Get Pro and Premium active subscribers
            result = await db.execute(
                select(User)
                .join(Subscription, Subscription.user_id == User.id)
                .join(SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id)
                .where(Subscription.status == "active")
                .where(SubscriptionPlan.name.in_(["Pro", "Premium"]))
                .where(User.is_active == True)
            )
            users = result.scalars().all()
            service = RecommendationService(db)
            total = 0
            for user in users:
                try:
                    recs = await service.refresh_for_user(user.id)
                    total += len(recs)
                except Exception as e:
                    logger.warning(f"[RecsTask] Failed for user {user.id}: {e}")
            await db.commit()
            logger.info(f"[RecsTask] Generated {total} recommendations for {len(users)} users")
            return total

    return run_async(_run())


# ── Task: Check Alerts ────────────────────────────────────────────────────────

@celery_app.task(name="app.workers.scheduler.task_check_alerts", bind=True)
def task_check_alerts(self):
    """Check all active alert rules against current trend scores."""
    async def _run():
        from app.db.base import AsyncSessionLocal
        from app.db.models.models import Alert, Trend
        from sqlalchemy import select, and_
        from datetime import datetime

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Alert, Trend)
                .join(Trend, Alert.trend_id == Trend.id)
                .where(Alert.is_active == True)
                .where(Alert.triggered == False)
                .where(Alert.trend_id.isnot(None))
            )
            rows = result.all()
            triggered_count = 0
            for alert, trend in rows:
                should_trigger = False
                if alert.alert_type == "trend_spike" and alert.threshold:
                    should_trigger = trend.trend_score >= alert.threshold
                elif alert.alert_type == "trend_decline" and alert.threshold:
                    should_trigger = trend.trend_score <= alert.threshold
                elif alert.alert_type == "new_trend":
                    should_trigger = trend.status == "emerging"

                if should_trigger:
                    alert.triggered = True
                    alert.triggered_at = datetime.utcnow()
                    alert.triggered_value = trend.trend_score
                    alert.message = (
                        f"Alert: {trend.name} reached score {trend.trend_score:.1f} "
                        f"({alert.alert_type.replace('_', ' ')})"
                    )
                    triggered_count += 1
                    # TODO: send notification via SendGrid/Twilio based on alert.channels

            await db.commit()
            if triggered_count:
                logger.info(f"[AlertTask] Triggered {triggered_count} alerts")
            return triggered_count

    return run_async(_run())


# ── Task: Daily Cleanup ───────────────────────────────────────────────────────

@celery_app.task(name="app.workers.scheduler.task_daily_cleanup", bind=True)
def task_daily_cleanup(self):
    """Remove raw posts older than 90 days and expired reports."""
    async def _run():
        from app.db.base import AsyncSessionLocal
        from app.db.models.models import RawPost, Report
        from sqlalchemy import select, delete
        from datetime import datetime, timedelta

        cutoff_posts = datetime.utcnow() - timedelta(days=90)
        cutoff_reports = datetime.utcnow()

        async with AsyncSessionLocal() as db:
            deleted_posts = await db.execute(
                delete(RawPost).where(RawPost.scraped_at < cutoff_posts)
            )
            deleted_reports = await db.execute(
                delete(Report).where(
                    Report.expires_at.isnot(None),
                    Report.expires_at < cutoff_reports,
                )
            )
            await db.commit()
            logger.info(
                f"[CleanupTask] Deleted {deleted_posts.rowcount} old posts "
                f"and {deleted_reports.rowcount} expired reports"
            )
            return {
                "deleted_posts": deleted_posts.rowcount,
                "deleted_reports": deleted_reports.rowcount,
            }

    return run_async(_run())
