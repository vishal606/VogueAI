from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.base import get_db
from app.db.models.models import User, Alert
from app.db.schemas.schemas import AlertCreate, AlertResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Alert).where(Alert.user_id == current_user.id).order_by(Alert.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(
    payload: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    alert = Alert(
        user_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Alert).where(and_(Alert.id == alert_id, Alert.user_id == current_user.id))
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.delete(alert)


@router.patch("/{alert_id}/toggle", response_model=AlertResponse)
async def toggle_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Alert).where(and_(Alert.id == alert_id, Alert.user_id == current_user.id))
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_active = not alert.is_active
    await db.flush()
    await db.refresh(alert)
    return alert
