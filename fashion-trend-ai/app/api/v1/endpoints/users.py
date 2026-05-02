from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.base import get_db
from app.db.models.models import User
from app.db.schemas.schemas import UserResponse, UserUpdate
from app.api.deps import get_current_user, require_admin, PaginationDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=204)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.is_active = False
    await db.flush()


# ── Admin routes ──────────────────────────────────────────────────────────────

@router.get("/", response_model=List[UserResponse], dependencies=[Depends(require_admin)])
async def list_users(
    pagination: PaginationDep = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).offset(pagination.offset).limit(pagination.page_size)
    )
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
