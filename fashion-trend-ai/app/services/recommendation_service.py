"""
RecommendationService — generates and manages personalised recommendations.
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.db.models.models import User, Recommendation, Trend
from app.services.ai_service import AIService
from app.utils.logger import logger


class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai = AIService(db)

    async def refresh_for_user(self, user_id: str) -> List[Recommendation]:
        """Delete stale recs and regenerate fresh ones."""
        # Clear old unread recs older than 7 days
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=7)
        old = await self.db.execute(
            select(Recommendation).where(
                and_(
                    Recommendation.user_id == user_id,
                    Recommendation.is_read == False,
                    Recommendation.created_at < cutoff,
                )
            )
        )
        for rec in old.scalars().all():
            await self.db.delete(rec)
        await self.db.flush()

        # Generate new recommendations
        new_recs = await self.ai.generate_recommendations_for_user(user_id)
        logger.info(f"Generated {len(new_recs)} recommendations for user {user_id}")
        return new_recs

    async def get_priority_actions(self, user_id: str, limit: int = 3) -> List[Recommendation]:
        """Top high-priority unread actions for a user."""
        result = await self.db.execute(
            select(Recommendation).where(
                and_(
                    Recommendation.user_id == user_id,
                    Recommendation.priority == "high",
                    Recommendation.is_read == False,
                )
            )
            .order_by(desc(Recommendation.confidence_score))
            .limit(limit)
        )
        return result.scalars().all()
