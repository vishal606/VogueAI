"""
AIService — orchestrates all 5 AI agents:
  Agent 1: Trend Collector     (see workers/scraper.py)
  Agent 2: Vision Analyzer     (vision_model.py)
  Agent 3: Trend Analyzer      (nlp_model.py)
  Agent 4: Forecast Agent      (forecasting.py)
  Agent 5: Business Advisor    (Claude API)
"""
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import anthropic

from app.db.models.models import Trend, TrendPrediction, Recommendation, RawPost
from app.db.schemas.schemas import (
    PredictionResponse, SeasonForecastResponse, AdvisorMessageResponse,
)
from app.core.config import settings
from app.utils.logger import logger


class AIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._anthropic = (
            anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            if settings.ANTHROPIC_API_KEY
            else None
        )

    # ── Agent 4: Forecast Agent ───────────────────────────────────────────────

    async def run_forecast_ensemble(
        self,
        trend_id: str,
        horizon_days: int = 30,
        models: List[str] = None,
    ) -> List[TrendPrediction]:
        """
        Ensemble of Prophet + LSTM + XGBoost predictions.
        Falls back to statistical simulation if torch/prophet not installed.
        """
        if models is None:
            models = ["prophet", "lstm", "xgboost"]

        # Fetch trend
        result = await self.db.execute(select(Trend).where(Trend.id == trend_id))
        trend = result.scalar_one_or_none()
        if not trend:
            raise ValueError(f"Trend {trend_id} not found")

        # Fetch historical predictions for context
        hist = await self.db.execute(
            select(TrendPrediction)
            .where(TrendPrediction.trend_id == trend_id)
            .order_by(TrendPrediction.prediction_date.desc())
            .limit(90)
        )
        history = hist.scalars().all()

        predictions = []
        for model_name in models:
            try:
                pred = await self._run_single_model(
                    trend=trend,
                    history=history,
                    model_name=model_name,
                    horizon_days=horizon_days,
                )
                predictions.append(pred)
                logger.info(f"[ForecastAgent] {model_name} prediction for '{trend.name}' complete")
            except Exception as e:
                logger.warning(f"[ForecastAgent] {model_name} failed: {e}, using fallback")
                pred = await self._statistical_fallback(trend, model_name, horizon_days)
                predictions.append(pred)

        # Persist
        for p in predictions:
            self.db.add(p)
        await self.db.flush()

        # Refresh
        for p in predictions:
            await self.db.refresh(p)

        return predictions

    async def _run_single_model(
        self,
        trend: Trend,
        history: list,
        model_name: str,
        horizon_days: int,
    ) -> TrendPrediction:
        """
        Dispatch to the appropriate forecasting model.
        Each model lives in app/ai/forecasting.py.
        """
        from app.ai.forecasting import ProphetForecaster, LSTMForecaster, XGBoostForecaster

        base_score = trend.trend_score
        growth = trend.growth_rate

        forecasters = {
            "prophet": ProphetForecaster(),
            "lstm": LSTMForecaster(),
            "xgboost": XGBoostForecaster(),
        }
        forecaster = forecasters.get(model_name)
        result = await forecaster.predict(
            current_score=base_score,
            growth_rate=growth,
            history=history,
            horizon_days=horizon_days,
        )
        season = self._get_season_label(horizon_days)
        return TrendPrediction(
            trend_id=trend.id,
            predicted_value=result["predicted_value"],
            prediction_date=date.today() + timedelta(days=horizon_days),
            confidence=result["confidence"],
            model_used=model_name,
            horizon_days=horizon_days,
            lower_bound=result.get("lower_bound"),
            upper_bound=result.get("upper_bound"),
            season=season,
            factors=result.get("factors", {}),
        )

    async def _statistical_fallback(
        self, trend: Trend, model_name: str, horizon_days: int
    ) -> TrendPrediction:
        """Simple exponential trend extrapolation when ML models unavailable."""
        import math
        decay = 0.95 if trend.status == "declining" else 1.0
        growth_factor = 1 + (trend.growth_rate / 100) * decay
        predicted = trend.trend_score * (growth_factor ** (horizon_days / 30))
        predicted = min(max(predicted, 0), 100)
        confidence = max(0.5, 0.9 - (horizon_days / 365) * 0.4)
        return TrendPrediction(
            trend_id=trend.id,
            predicted_value=round(predicted, 2),
            prediction_date=date.today() + timedelta(days=horizon_days),
            confidence=round(confidence, 2),
            model_used=f"{model_name}_fallback",
            horizon_days=horizon_days,
            lower_bound=round(predicted * 0.85, 2),
            upper_bound=round(predicted * 1.15, 2),
            season=self._get_season_label(horizon_days),
            factors={"method": "exponential_extrapolation", "growth_rate": trend.growth_rate},
        )

    def _get_season_label(self, horizon_days: int) -> str:
        future = date.today() + timedelta(days=horizon_days)
        month = future.month
        year = future.year
        if month in (3, 4, 5):
            return f"Spring {year}"
        elif month in (6, 7, 8):
            return f"Summer {year}"
        elif month in (9, 10, 11):
            return f"Fall {year}"
        return f"Winter {year}"

    # ── Season Forecasts ──────────────────────────────────────────────────────

    async def get_season_forecasts(self) -> List[SeasonForecastResponse]:
        """
        Pull top predictions per season from DB,
        enriched with Claude-generated descriptions.
        """
        result = await self.db.execute(
            select(TrendPrediction, Trend)
            .join(Trend, TrendPrediction.trend_id == Trend.id)
            .order_by(desc(TrendPrediction.confidence))
            .limit(9)
        )
        rows = result.all()
        forecasts = []
        for pred, trend in rows:
            description = await self._generate_trend_description(trend, pred)
            forecasts.append(
                SeasonForecastResponse(
                    season=pred.season or "Unknown Season",
                    trend_name=trend.name,
                    confidence=round(pred.confidence * 100, 1),
                    description=description,
                    predicted_score=pred.predicted_value,
                    key_factors=list(pred.factors.keys())[:3],
                )
            )
        return forecasts

    async def _generate_trend_description(self, trend: Trend, pred: TrendPrediction) -> str:
        if not self._anthropic:
            return f"{trend.name} is predicted to reach a score of {pred.predicted_value:.0f} by {pred.season}."
        try:
            msg = await self._anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=120,
                system="You are a fashion trend analyst. Write one sentence (max 25 words) describing a predicted fashion trend. Be specific and editorial.",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Trend: {trend.name}, Category: {trend.category}, "
                            f"Score: {pred.predicted_value:.0f}/100, "
                            f"Season: {pred.season}, Confidence: {pred.confidence*100:.0f}%"
                        ),
                    }
                ],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            logger.warning(f"Claude description generation failed: {e}")
            return f"{trend.name} is projected to dominate {pred.season} collections."

    # ── Agent 5: Business Advisor ─────────────────────────────────────────────

    async def get_advisor_response(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AdvisorMessageResponse:
        """
        Claude-powered AI advisor with live trend context injected into system prompt.
        """
        # Inject live trend data as context
        trend_context = await self._build_trend_context()

        system_prompt = f"""You are an expert AI Fashion Business Advisor for boutique owners and online fashion stores.
You have access to real-time fashion trend data. Use it to give specific, actionable advice.

CURRENT TREND DATA (as of {date.today()}):
{trend_context}

GUIDELINES:
- Be concise and actionable (under 200 words)
- Use specific trend names and scores from the data
- Always connect advice to inventory or business decisions
- Mention confidence levels for predictions
- Format with clear bullet points when listing items
"""
        if not self._anthropic:
            return AdvisorMessageResponse(
                response="AI Advisor is not configured. Please set ANTHROPIC_API_KEY in your .env file.",
                sources_used=[],
                related_trends=[],
                suggested_actions=["Configure ANTHROPIC_API_KEY"],
            )

        try:
            msg = await self._anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": message}],
            )
            response_text = msg.content[0].text.strip()

            # Extract related trends from DB
            related = await self._find_related_trends(message)

            return AdvisorMessageResponse(
                response=response_text,
                sources_used=["Instagram", "TikTok", "Pinterest", "E-commerce"],
                related_trends=[t.name for t in related],
                suggested_actions=self._extract_actions(response_text),
            )
        except Exception as e:
            logger.error(f"Advisor API error: {e}")
            raise

    async def _build_trend_context(self) -> str:
        result = await self.db.execute(
            select(Trend).order_by(desc(Trend.trend_score)).limit(10)
        )
        trends = result.scalars().all()
        lines = ["Top Trends:"]
        for t in trends:
            lines.append(
                f"  - {t.name} ({t.category}): score={t.trend_score:.1f}, "
                f"growth={t.growth_rate:+.1f}%, status={t.status}, region={t.region}"
            )
        return "\n".join(lines)

    async def _find_related_trends(self, message: str) -> List[Trend]:
        from sqlalchemy import or_
        words = [w for w in message.lower().split() if len(w) > 3][:5]
        if not words:
            return []
        conditions = [Trend.name.ilike(f"%{w}%") for w in words]
        result = await self.db.execute(
            select(Trend).where(or_(*conditions)).limit(3)
        )
        return result.scalars().all()

    def _extract_actions(self, text: str) -> List[str]:
        """Extract bullet-point actions from advisor response."""
        actions = []
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith(("-", "•", "*", "1.", "2.", "3.")):
                clean = stripped.lstrip("-•*0123456789. ").strip()
                if clean and len(clean) > 10:
                    actions.append(clean)
        return actions[:4]

    # ── Agent 5: Generate Recommendations ────────────────────────────────────

    async def generate_recommendations_for_user(self, user_id: str) -> List[Recommendation]:
        """
        For each top rising trend, generate a recommendation for the user
        using Claude to reason about the action.
        """
        result = await self.db.execute(
            select(Trend)
            .where(Trend.status.in_(["rising", "emerging"]))
            .order_by(desc(Trend.growth_rate))
            .limit(5)
        )
        trends = result.scalars().all()
        recs = []
        for trend in trends:
            action, description, priority, reasoning = await self._advise_action(trend)
            rec = Recommendation(
                user_id=user_id,
                trend_id=trend.id,
                action=action,
                description=description,
                priority=priority,
                confidence_score=trend.trend_score / 100,
                ai_reasoning=reasoning,
            )
            self.db.add(rec)
            recs.append(rec)

        await self.db.flush()
        return recs

    async def _advise_action(self, trend: Trend):
        """Use simple heuristics + optional Claude reasoning."""
        if trend.trend_score >= 80 and trend.growth_rate >= 30:
            action, priority = "stock_now", "high"
            description = f"{trend.name} is peaking — stock immediately for maximum revenue."
        elif trend.trend_score >= 60 and trend.growth_rate >= 15:
            action, priority = "monitor", "medium"
            description = f"{trend.name} is rising steadily — plan sourcing within 2 weeks."
        elif trend.growth_rate < -10:
            action, priority = "reduce_inventory", "high"
            description = f"{trend.name} is declining — clear existing stock with promotions."
        else:
            action, priority = "monitor", "low"
            description = f"{trend.name} shows early signals — watch for 1–2 more weeks."

        reasoning = None
        if self._anthropic:
            try:
                msg = await self._anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=80,
                    system="You are a fashion business advisor. In one sentence, explain why a boutique owner should take the given action for this trend.",
                    messages=[
                        {
                            "role": "user",
                            "content": (
                                f"Trend: {trend.name}, Score: {trend.trend_score:.0f}, "
                                f"Growth: {trend.growth_rate:+.1f}%, Action: {action}"
                            ),
                        }
                    ],
                )
                reasoning = msg.content[0].text.strip()
            except Exception:
                pass

        return action, description, priority, reasoning
