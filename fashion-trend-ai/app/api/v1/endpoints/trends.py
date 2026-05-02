from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc

from app.db.base import get_db
from app.db.models.models import User, Trend
from app.db.schemas.schemas import (
    TrendCreate, TrendUpdate, TrendResponse,
    TrendListResponse, DashboardSummaryResponse,
)
from app.api.deps import get_current_user, require_admin, PaginationDep
from app.services.trend_service import TrendService
from app.utils.logger import logger

router = APIRouter(prefix="/trends", tags=["Trends"])


@router.get("/", response_model=TrendListResponse)
async def list_trends(
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query(default="trend_score", enum=["trend_score", "growth_rate", "date", "name"]),
    sort_order: str = Query(default="desc", enum=["asc", "desc"]),
    pagination: PaginationDep = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all trends with advanced filtering.
    Accessible to all authenticated users.
    """
    filters = []
    if category:
        filters.append(Trend.category == category)
    if region:
        filters.append(Trend.region == region)
    if status:
        filters.append(Trend.status == status)
    if min_score is not None:
        filters.append(Trend.trend_score >= min_score)
    if date_from:
        filters.append(Trend.date >= date_from)
    if date_to:
        filters.append(Trend.date <= date_to)
    if search:
        filters.append(
            or_(
                Trend.name.ilike(f"%{search}%"),
                Trend.category.ilike(f"%{search}%"),
            )
        )

    sort_col = getattr(Trend, sort_by)
    order_fn = desc if sort_order == "desc" else lambda c: c

    count_q = select(func.count()).select_from(Trend)
    if filters:
        count_q = count_q.where(and_(*filters))
    total = (await db.execute(count_q)).scalar()

    q = select(Trend)
    if filters:
        q = q.where(and_(*filters))
    q = q.order_by(order_fn(sort_col)).offset(pagination.offset).limit(pagination.page_size)
    trends = (await db.execute(q)).scalars().all()

    return TrendListResponse(
        trends=trends,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        has_next=(pagination.offset + pagination.page_size) < total,
    )


@router.get("/dashboard", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard summary with stats and top trends."""
    service = TrendService(db)
    return await service.get_dashboard_summary()


@router.get("/categories", response_model=List[str])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Trend.category).distinct())
    return [r[0] for r in result.all()]


@router.get("/rising", response_model=List[TrendResponse])
async def get_rising_trends(
    limit: int = Query(default=10, ge=1, le=50),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get currently rising trends ordered by growth rate."""
    filters = [Trend.status.in_(["rising", "emerging"])]
    if region:
        filters.append(Trend.region == region)

    result = await db.execute(
        select(Trend)
        .where(and_(*filters))
        .order_by(desc(Trend.growth_rate))
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{trend_id}", response_model=TrendResponse)
async def get_trend(
    trend_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend


@router.post("/", response_model=TrendResponse, status_code=201)
async def create_trend(
    payload: TrendCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    trend = Trend(**payload.model_dump())
    db.add(trend)
    await db.flush()
    await db.refresh(trend)
    return trend


@router.patch("/{trend_id}", response_model=TrendResponse)
async def update_trend(
    trend_id: str,
    payload: TrendUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(trend, k, v)
    await db.flush()
    await db.refresh(trend)
    return trend


@router.delete("/{trend_id}", status_code=204)
async def delete_trend(
    trend_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    await db.delete(trend)
