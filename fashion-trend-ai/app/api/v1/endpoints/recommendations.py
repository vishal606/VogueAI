"""
recommendations.py — Business Advisor recommendations endpoint
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.db.base import get_db
from app.db.models.models import User, Recommendation
from app.db.schemas.schemas import RecommendationResponse, RecommendationUpdate
from app.api.deps import get_current_user, require_plan

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/", response_model=List[RecommendationResponse])
async def list_recommendations(
    priority: Optional[str] = Query(None, enum=["high", "medium", "low"]),
    action: Optional[str] = Query(None),
    unread_only: bool = Query(default=False),
    _sub=Depends(require_plan("Pro", "Premium")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get personalised AI recommendations. Requires Pro+."""
    filters = [Recommendation.user_id == current_user.id]
    if priority:
        filters.append(Recommendation.priority == priority)
    if action:
        filters.append(Recommendation.action == action)
    if unread_only:
        filters.append(Recommendation.is_read == False)

    result = await db.execute(
        select(Recommendation)
        .where(and_(*filters))
        .order_by(desc(Recommendation.created_at))
    )
    return result.scalars().all()


@router.patch("/{rec_id}", response_model=RecommendationResponse)
async def mark_recommendation(
    rec_id: str,
    payload: RecommendationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Recommendation).where(
            and_(Recommendation.id == rec_id, Recommendation.user_id == current_user.id)
        )
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.is_read = payload.is_read
    await db.flush()
    await db.refresh(rec)
    return rec
