from typing import Optional
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.db.models.models import User, Subscription, SubscriptionPlan
from app.core.security import get_current_user_id


# ── Current User ──────────────────────────────────────────────────────────────

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ── Subscription Guard ────────────────────────────────────────────────────────

async def get_active_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Optional[Subscription]:
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status == "active")
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def require_plan(*plan_names: str):
    """
    Usage:
        @router.get("/ai-recommendations")
        async def endpoint(
            sub=Depends(require_plan("Pro", "Premium"))
        ):
    """
    async def _check(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> Subscription:
        result = await db.execute(
            select(Subscription)
            .join(SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id)
            .where(Subscription.user_id == current_user.id)
            .where(Subscription.status == "active")
            .where(SubscriptionPlan.name.in_(plan_names))
        )
        sub = result.scalar_one_or_none()
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"This feature requires one of: {list(plan_names)}",
            )
        return sub

    return _check


# ── Pagination ────────────────────────────────────────────────────────────────

class PaginationDep:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
