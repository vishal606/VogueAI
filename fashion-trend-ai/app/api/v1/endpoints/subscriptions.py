import stripe
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.db.models.models import User, Subscription, SubscriptionPlan
from app.db.schemas.schemas import (
    SubscriptionCreate, SubscriptionResponse, PlanResponse,
)
from app.api.deps import get_current_user
from app.core.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_PRICE_MAP = {
    "Basic": settings.STRIPE_PRICE_BASIC,
    "Pro": settings.STRIPE_PRICE_PRO,
    "Premium": settings.STRIPE_PRICE_PREMIUM,
}


# ── Plans ─────────────────────────────────────────────────────────────────────

@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(db: AsyncSession = Depends(get_db)):
    """Public endpoint — list all active subscription plans."""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.is_active == True)
    )
    return result.scalars().all()


# ── Current Subscription ──────────────────────────────────────────────────────

@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status == "active")
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return sub


# ── Create Subscription (Stripe) ──────────────────────────────────────────────

@router.post("/", response_model=dict, status_code=201)
async def create_subscription(
    payload: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Stripe subscription.
    Returns a Stripe client_secret for frontend payment confirmation.
    """
    # Fetch plan
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == payload.plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if not settings.STRIPE_SECRET_KEY:
        # Dev mode: create subscription directly without Stripe
        sub = Subscription(
            user_id=current_user.id,
            plan_id=plan.id,
            status="active",
        )
        db.add(sub)
        await db.flush()
        await db.refresh(sub)
        return {"subscription_id": sub.id, "status": "active", "dev_mode": True}

    try:
        # Ensure Stripe customer exists
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.name,
                metadata={"user_id": current_user.id},
            )
            current_user.stripe_customer_id = customer.id
            await db.flush()

        # Create Stripe subscription
        stripe_sub = stripe.Subscription.create(
            customer=current_user.stripe_customer_id,
            items=[{"price": plan.stripe_price_id}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
        )

        # Store in DB (pending until webhook confirms)
        sub = Subscription(
            user_id=current_user.id,
            plan_id=plan.id,
            status="trialing" if stripe_sub.status == "trialing" else "pending",
            stripe_subscription_id=stripe_sub.id,
        )
        db.add(sub)
        await db.flush()

        return {
            "subscription_id": sub.id,
            "stripe_subscription_id": stripe_sub.id,
            "client_secret": stripe_sub.latest_invoice.payment_intent.client_secret,
            "status": stripe_sub.status,
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ── Cancel Subscription ───────────────────────────────────────────────────────

@router.delete("/me", status_code=200)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status == "active")
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription")

    if sub.stripe_subscription_id and settings.STRIPE_SECRET_KEY:
        stripe.Subscription.modify(sub.stripe_subscription_id, cancel_at_period_end=True)

    sub.status = "canceled"
    await db.flush()
    return {"message": "Subscription will be canceled at end of billing period"}


# ── Stripe Webhook ────────────────────────────────────────────────────────────

@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "invoice.payment_succeeded":
        stripe_sub_id = data.get("subscription")
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = "active"
            await db.flush()

    elif event_type == "customer.subscription.deleted":
        stripe_sub_id = data.get("id")
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = "canceled"
            await db.flush()

    elif event_type == "invoice.payment_failed":
        stripe_sub_id = data.get("subscription")
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = "past_due"
            await db.flush()

    logger.info(f"Stripe webhook processed: {event_type}")
    return {"received": True}
