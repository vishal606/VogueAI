"""
Fashion Trend AI — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.db.base import init_db, close_db
from app.api.v1.router import api_router
from app.utils.logger import logger


# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    await init_db()
    await _seed_subscription_plans()
    logger.info("✅ Database initialised")
    yield
    await close_db()
    logger.info("🛑 Application shutdown complete")


# ── App Factory ───────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI-Powered Fashion Trend Prediction Platform. "
            "Multi-agent system collecting, analysing and forecasting fashion trends "
            "from social media and e-commerce for boutique owners and fashion stores."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # ── Health Check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "docs": "/docs",
            "version": settings.APP_VERSION,
        }

    # ── Exception Handlers ────────────────────────────────────────────────────
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "Resource not found", "path": str(request.url)},
        )

    @app.exception_handler(500)
    async def server_error_handler(request: Request, exc):
        logger.error(f"Internal Server Error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."},
        )

    return app


# ── Seed Subscription Plans ───────────────────────────────────────────────────
async def _seed_subscription_plans():
    """Insert default plans if they don't exist yet."""
    from app.db.base import AsyncSessionLocal
    from app.db.models.models import SubscriptionPlan
    from sqlalchemy import select

    plans = [
        {
            "name": "Basic",
            "type": "monthly",
            "price": 49.00,
            "features": {
                "weekly_trends": True,
                "top_colors": True,
                "basic_reports": True,
                "predictions": False,
                "detailed_insights": False,
                "custom_reports": False,
                "ai_recommendations": False,
                "custom_alerts": False,
                "api_access": False,
                "max_users": 1,
            },
            "stripe_price_id": settings.STRIPE_PRICE_BASIC,
        },
        {
            "name": "Pro",
            "type": "monthly",
            "price": 149.00,
            "features": {
                "weekly_trends": True,
                "top_colors": True,
                "basic_reports": True,
                "predictions": True,
                "detailed_insights": True,
                "custom_reports": True,
                "ai_recommendations": True,
                "custom_alerts": False,
                "api_access": True,
                "max_users": 5,
            },
            "stripe_price_id": settings.STRIPE_PRICE_PRO,
        },
        {
            "name": "Premium",
            "type": "monthly",
            "price": 399.00,
            "features": {
                "weekly_trends": True,
                "top_colors": True,
                "basic_reports": True,
                "predictions": True,
                "detailed_insights": True,
                "custom_reports": True,
                "ai_recommendations": True,
                "custom_alerts": True,
                "api_access": True,
                "competitor_tracking": True,
                "white_label_reports": True,
                "max_users": -1,  # unlimited
            },
            "stripe_price_id": settings.STRIPE_PRICE_PREMIUM,
        },
    ]

    async with AsyncSessionLocal() as db:
        for plan_data in plans:
            existing = await db.execute(
                select(SubscriptionPlan).where(SubscriptionPlan.name == plan_data["name"])
            )
            if not existing.scalar_one_or_none():
                plan = SubscriptionPlan(**plan_data)
                db.add(plan)
        await db.commit()
        logger.info("✅ Subscription plans seeded")


# ── Entry Point ───────────────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        workers=1 if settings.DEBUG else 4,
    )
