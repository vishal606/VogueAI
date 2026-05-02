from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.trends import router as trends_router
from app.api.v1.endpoints.predictions import router as predictions_router
from app.api.v1.endpoints.recommendations import router as recommendations_router
from app.api.v1.endpoints.alerts import router as alerts_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.subscriptions import router as subscriptions_router
from app.api.v1.endpoints.advisor import (
    advisor_router, scraper_router, colors_router
)

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(trends_router)
api_router.include_router(predictions_router)
api_router.include_router(recommendations_router)
api_router.include_router(alerts_router)
api_router.include_router(reports_router)
api_router.include_router(subscriptions_router)
api_router.include_router(advisor_router)
api_router.include_router(scraper_router)
api_router.include_router(colors_router)

from app.api.v1.endpoints.payments import router as payments_router
api_router.include_router(payments_router)
