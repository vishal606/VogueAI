from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.base import get_db
from app.db.models.models import User, Report
from app.db.schemas.schemas import ReportCreate, ReportResponse
from app.api.deps import get_current_user, require_plan
from app.services.trend_service import TrendService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report)
        .where(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=ReportResponse, status_code=202)
async def generate_report(
    payload: ReportCreate,
    background_tasks: BackgroundTasks,
    _sub=Depends(require_plan("Pro", "Premium")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Queue a report for generation.
    Returns immediately with status=pending; background task generates the file.
    """
    report = Report(
        user_id=current_user.id,
        title=payload.title,
        report_type=payload.report_type,
        filters=payload.filters,
        status="pending",
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    # Fire background job
    service = TrendService(db)
    background_tasks.add_task(service.generate_report, report.id, payload)
    return report


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report).where(
            and_(Report.id == report_id, Report.user_id == current_user.id)
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/{report_id}", status_code=204)
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report).where(
            and_(Report.id == report_id, Report.user_id == current_user.id)
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    await db.delete(report)
