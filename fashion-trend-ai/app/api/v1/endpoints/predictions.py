from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.db.models.models import User, Trend, TrendPrediction
from app.db.schemas.schemas import (
    PredictionResponse, PredictionRequest, SeasonForecastResponse,
)
from app.api.deps import get_current_user, require_plan
from app.services.ai_service import AIService

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("/", response_model=List[PredictionResponse])
async def list_predictions(
    trend_id: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List predictions. Available to Basic+ plans."""
    q = select(TrendPrediction).order_by(desc(TrendPrediction.created_at))
    if trend_id:
        q = q.where(TrendPrediction.trend_id == trend_id)
    if model:
        q = q.where(TrendPrediction.model_used == model)
    q = q.limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/generate", response_model=List[PredictionResponse])
async def generate_prediction(
    payload: PredictionRequest,
    background_tasks: BackgroundTasks,
    _sub=Depends(require_plan("Pro", "Premium")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger AI prediction for a specific trend.
    Runs Prophet + LSTM + XGBoost ensemble.
    Requires Pro or Premium subscription.
    """
    # Validate trend exists
    result = await db.execute(select(Trend).where(Trend.id == payload.trend_id))
    trend = result.scalar_one_or_none()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    ai_service = AIService(db)
    predictions = await ai_service.run_forecast_ensemble(
        trend_id=payload.trend_id,
        horizon_days=payload.horizon_days,
        models=payload.models,
    )
    return predictions


@router.get("/seasons", response_model=List[SeasonForecastResponse])
async def get_season_forecasts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated season-level forecasts."""
    ai_service = AIService(db)
    return await ai_service.get_season_forecasts()


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TrendPrediction).where(TrendPrediction.id == prediction_id)
    )
    pred = result.scalar_one_or_none()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return pred
