"""
Tests for subscriptions, alerts, reports, users, and predictions endpoints.
"""
import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Trend, Alert, Report, SubscriptionPlan
from tests.conftest import auth_headers


# ── Helper ────────────────────────────────────────────────────────────────────

async def seed_trend(db: AsyncSession, **kwargs) -> Trend:
    defaults = dict(
        name="Test Trend",
        category="Style",
        trend_score=75.0,
        growth_rate=20.0,
        region="Global",
        status="rising",
        date=date.today(),
    )
    defaults.update(kwargs)
    t = Trend(**defaults)
    db.add(t)
    await db.flush()
    await db.refresh(t)
    return t


# ═══════════════════════════════════════════════════════════════
# SUBSCRIPTIONS
# ═══════════════════════════════════════════════════════════════

class TestSubscriptions:

    @pytest.mark.asyncio
    async def test_list_plans_public(self, client: AsyncClient, db_session: AsyncSession):
        plan = SubscriptionPlan(
            name="Basic",
            type="monthly",
            price=49.00,
            features={"weekly_trends": True},
            is_active=True,
        )
        db_session.add(plan)
        await db_session.flush()

        response = await client.get("/api/v1/subscriptions/plans")
        assert response.status_code == 200
        plans = response.json()
        assert isinstance(plans, list)
        assert any(p["name"] == "Basic" for p in plans)

    @pytest.mark.asyncio
    async def test_get_my_subscription_no_sub(self, client: AsyncClient, basic_token):
        response = await client.get(
            "/api/v1/subscriptions/me",
            headers=auth_headers(basic_token),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_my_subscription_with_sub(self, client: AsyncClient, pro_token):
        response = await client.get(
            "/api/v1/subscriptions/me",
            headers=auth_headers(pro_token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_create_subscription_dev_mode(
        self, client: AsyncClient, basic_token, db_session: AsyncSession
    ):
        plan = SubscriptionPlan(
            name="TestPlan",
            type="monthly",
            price=29.00,
            features={},
            is_active=True,
        )
        db_session.add(plan)
        await db_session.flush()
        await db_session.refresh(plan)

        response = await client.post(
            "/api/v1/subscriptions/",
            headers=auth_headers(basic_token),
            json={"plan_id": plan.id},
        )
        assert response.status_code == 201
        data = response.json()
        assert "subscription_id" in data


# ═══════════════════════════════════════════════════════════════
# ALERTS
# ═══════════════════════════════════════════════════════════════

class TestAlerts:

    @pytest.mark.asyncio
    async def test_list_alerts_empty(self, client: AsyncClient, basic_token):
        response = await client.get(
            "/api/v1/alerts/",
            headers=auth_headers(basic_token),
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_alert(self, client: AsyncClient, basic_token, db_session: AsyncSession):
        trend = await seed_trend(db_session)
        response = await client.post(
            "/api/v1/alerts/",
            headers=auth_headers(basic_token),
            json={
                "trend_id": trend.id,
                "alert_type": "trend_spike",
                "threshold": 90.0,
                "channels": ["email"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["alert_type"] == "trend_spike"
        assert data["threshold"] == 90.0
        assert data["triggered"] is False

    @pytest.mark.asyncio
    async def test_create_alert_invalid_channel(self, client: AsyncClient, basic_token):
        response = await client.post(
            "/api/v1/alerts/",
            headers=auth_headers(basic_token),
            json={
                "alert_type": "new_trend",
                "channels": ["telegram"],  # invalid
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_alert(self, client: AsyncClient, basic_token, db_session: AsyncSession, basic_user):
        alert = Alert(
            user_id=basic_user.id,
            alert_type="new_trend",
            channels=["email"],
            is_active=True,
        )
        db_session.add(alert)
        await db_session.flush()
        await db_session.refresh(alert)

        response = await client.delete(
            f"/api/v1/alerts/{alert.id}",
            headers=auth_headers(basic_token),
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_toggle_alert(self, client: AsyncClient, basic_token, db_session: AsyncSession, basic_user):
        alert = Alert(
            user_id=basic_user.id,
            alert_type="trend_spike",
            channels=["email"],
            is_active=True,
        )
        db_session.add(alert)
        await db_session.flush()
        await db_session.refresh(alert)

        response = await client.patch(
            f"/api/v1/alerts/{alert.id}/toggle",
            headers=auth_headers(basic_token),
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_cannot_delete_other_users_alert(
        self, client: AsyncClient, pro_token, db_session: AsyncSession, basic_user
    ):
        alert = Alert(
            user_id=basic_user.id,
            alert_type="new_trend",
            channels=["email"],
            is_active=True,
        )
        db_session.add(alert)
        await db_session.flush()
        await db_session.refresh(alert)

        response = await client.delete(
            f"/api/v1/alerts/{alert.id}",
            headers=auth_headers(pro_token),
        )
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════════

class TestReports:

    @pytest.mark.asyncio
    async def test_list_reports_empty(self, client: AsyncClient, pro_token):
        response = await client.get(
            "/api/v1/reports/",
            headers=auth_headers(pro_token),
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_generate_report_pro(self, client: AsyncClient, pro_token):
        response = await client.post(
            "/api/v1/reports/",
            headers=auth_headers(pro_token),
            json={
                "title": "Weekly Trends April 2025",
                "report_type": "weekly_trends",
                "filters": {"region": "Global"},
            },
        )
        assert response.status_code == 202
        data = response.json()
        assert data["title"] == "Weekly Trends April 2025"
        assert data["status"] == "pending"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_generate_report_forbidden_basic(self, client: AsyncClient, basic_token):
        response = await client.post(
            "/api/v1/reports/",
            headers=auth_headers(basic_token),
            json={
                "title": "Blocked Report",
                "report_type": "weekly_trends",
            },
        )
        assert response.status_code == 402

    @pytest.mark.asyncio
    async def test_get_report_by_id(self, client: AsyncClient, pro_token, pro_user, db_session: AsyncSession):
        report = Report(
            user_id=pro_user.id,
            title="Color Palette Q2",
            report_type="color_palette",
            status="ready",
            filters={},
            data_snapshot={"colors": []},
        )
        db_session.add(report)
        await db_session.flush()
        await db_session.refresh(report)

        response = await client.get(
            f"/api/v1/reports/{report.id}",
            headers=auth_headers(pro_token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report.id
        assert data["status"] == "ready"

    @pytest.mark.asyncio
    async def test_cannot_access_other_users_report(
        self, client: AsyncClient, basic_token, pro_user, db_session: AsyncSession
    ):
        report = Report(
            user_id=pro_user.id,
            title="Private Report",
            report_type="weekly_trends",
            status="ready",
            filters={},
            data_snapshot={},
        )
        db_session.add(report)
        await db_session.flush()
        await db_session.refresh(report)

        response = await client.get(
            f"/api/v1/reports/{report.id}",
            headers=auth_headers(basic_token),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_report(self, client: AsyncClient, pro_token, pro_user, db_session: AsyncSession):
        report = Report(
            user_id=pro_user.id,
            title="To Delete",
            report_type="custom",
            status="ready",
            filters={},
            data_snapshot={},
        )
        db_session.add(report)
        await db_session.flush()
        await db_session.refresh(report)

        response = await client.delete(
            f"/api/v1/reports/{report.id}",
            headers=auth_headers(pro_token),
        )
        assert response.status_code == 204


# ═══════════════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════════════

class TestUsers:

    @pytest.mark.asyncio
    async def test_get_my_profile(self, client: AsyncClient, basic_token, basic_user):
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers(basic_token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == basic_user.email
        assert data["name"] == basic_user.name

    @pytest.mark.asyncio
    async def test_update_profile_name(self, client: AsyncClient, basic_token):
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers(basic_token),
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_deactivate_account(self, client: AsyncClient, db_session: AsyncSession):
        from app.db.models.models import User
        from app.core.security import hash_password, create_access_token

        user = User(
            name="Temp User",
            email="temp_delete@test.com",
            password_hash=hash_password("password123"),
            role="boutique_owner",
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)
        token = create_access_token(user.id)

        response = await client.delete(
            "/api/v1/users/me",
            headers=auth_headers(token),
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_admin_list_users(self, client: AsyncClient, admin_token, basic_user):
        response = await client.get(
            "/api/v1/users/",
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)

    @pytest.mark.asyncio
    async def test_non_admin_cannot_list_users(self, client: AsyncClient, basic_token):
        response = await client.get(
            "/api/v1/users/",
            headers=auth_headers(basic_token),
        )
        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════
# RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════

class TestRecommendations:

    @pytest.mark.asyncio
    async def test_list_recommendations_pro(self, client: AsyncClient, pro_token):
        response = await client.get(
            "/api/v1/recommendations/",
            headers=auth_headers(pro_token),
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_recommendations_blocked_basic(self, client: AsyncClient, basic_token):
        response = await client.get(
            "/api/v1/recommendations/",
            headers=auth_headers(basic_token),
        )
        assert response.status_code == 402

    @pytest.mark.asyncio
    async def test_mark_recommendation_read(
        self, client: AsyncClient, pro_token, pro_user, db_session: AsyncSession
    ):
        from app.db.models.models import Recommendation

        trend = await seed_trend(db_session, name="Rec Trend")
        rec = Recommendation(
            user_id=pro_user.id,
            trend_id=trend.id,
            action="stock_now",
            description="Stock immediately",
            priority="high",
            confidence_score=0.9,
            is_read=False,
        )
        db_session.add(rec)
        await db_session.flush()
        await db_session.refresh(rec)

        response = await client.patch(
            f"/api/v1/recommendations/{rec.id}",
            headers=auth_headers(pro_token),
            json={"is_read": True},
        )
        assert response.status_code == 200
        assert response.json()["is_read"] is True
