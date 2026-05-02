import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Trend
from tests.conftest import auth_headers


async def create_test_trend(db: AsyncSession, **kwargs) -> Trend:
    defaults = dict(
        name="Quiet Luxury",
        category="Style",
        trend_score=88.5,
        growth_rate=32.0,
        region="Global",
        status="rising",
        date=date.today(),
        color_hex="#C9A96E",
        top_hashtags=["quietluxury", "minimalist"],
        source_breakdown={"instagram": {"normalized_score": 0.8}},
    )
    defaults.update(kwargs)
    trend = Trend(**defaults)
    db.add(trend)
    await db.flush()
    await db.refresh(trend)
    return trend


# ── List Trends ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_trends_authenticated(client: AsyncClient, basic_token, db_session):
    await create_test_trend(db_session, name="Butter Yellow", category="Color")
    response = await client.get(
        "/api/v1/trends/",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
    assert "total" in data
    assert isinstance(data["trends"], list)


@pytest.mark.asyncio
async def test_list_trends_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/trends/")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_trends_filter_category(client: AsyncClient, basic_token, db_session):
    await create_test_trend(db_session, name="Cobalt Blue", category="Color")
    await create_test_trend(db_session, name="Micro Pleats", category="Texture")

    response = await client.get(
        "/api/v1/trends/?category=Color",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    data = response.json()
    for trend in data["trends"]:
        assert trend["category"] == "Color"


@pytest.mark.asyncio
async def test_list_trends_filter_status(client: AsyncClient, basic_token, db_session):
    await create_test_trend(db_session, name="Rising Trend", status="rising")
    await create_test_trend(db_session, name="Peak Trend", status="peak")

    response = await client.get(
        "/api/v1/trends/?status=rising",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    data = response.json()
    for trend in data["trends"]:
        assert trend["status"] == "rising"


@pytest.mark.asyncio
async def test_list_trends_search(client: AsyncClient, basic_token, db_session):
    await create_test_trend(db_session, name="Sculptural Bags")
    response = await client.get(
        "/api/v1/trends/?search=sculptural",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    data = response.json()
    names = [t["name"].lower() for t in data["trends"]]
    assert any("sculptural" in n for n in names)


@pytest.mark.asyncio
async def test_list_trends_pagination(client: AsyncClient, basic_token, db_session):
    for i in range(5):
        await create_test_trend(db_session, name=f"Trend {i}")

    response = await client.get(
        "/api/v1/trends/?page=1&page_size=2",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["trends"]) <= 2
    assert data["page"] == 1
    assert data["page_size"] == 2


@pytest.mark.asyncio
async def test_list_trends_sort_by_score(client: AsyncClient, basic_token, db_session):
    await create_test_trend(db_session, name="Low Score", trend_score=20.0)
    await create_test_trend(db_session, name="High Score", trend_score=95.0)

    response = await client.get(
        "/api/v1/trends/?sort_by=trend_score&sort_order=desc",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    scores = [t["trend_score"] for t in response.json()["trends"]]
    assert scores == sorted(scores, reverse=True)


# ── Single Trend ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_trend_by_id(client: AsyncClient, basic_token, db_session):
    trend = await create_test_trend(db_session, name="Neo Bohemian")
    response = await client.get(
        f"/api/v1/trends/{trend.id}",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == trend.id
    assert data["name"] == "Neo Bohemian"


@pytest.mark.asyncio
async def test_get_trend_not_found(client: AsyncClient, basic_token):
    response = await client.get(
        "/api/v1/trends/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 404


# ── Rising Trends ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_rising_trends(client: AsyncClient, basic_token, db_session):
    await create_test_trend(db_session, name="Rising 1", status="rising", growth_rate=45.0)
    await create_test_trend(db_session, name="Declining 1", status="declining", growth_rate=-10.0)

    response = await client.get(
        "/api/v1/trends/rising",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    statuses = [t["status"] for t in response.json()]
    assert all(s in ("rising", "emerging") for s in statuses)


# ── Categories ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_categories(client: AsyncClient, basic_token, db_session):
    await create_test_trend(db_session, name="Style T", category="Style")
    await create_test_trend(db_session, name="Color T", category="Color")

    response = await client.get(
        "/api/v1/trends/categories",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    cats = response.json()
    assert isinstance(cats, list)
    assert "Style" in cats or "Color" in cats


# ── Admin CRUD ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_trend_admin(client: AsyncClient, admin_token):
    response = await client.post(
        "/api/v1/trends/",
        headers=auth_headers(admin_token),
        json={
            "name": "Admin Created Trend",
            "category": "Accessory",
            "region": "Europe",
            "trend_score": 72.0,
            "growth_rate": 18.5,
            "status": "emerging",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Admin Created Trend"
    assert data["category"] == "Accessory"


@pytest.mark.asyncio
async def test_create_trend_forbidden_for_basic(client: AsyncClient, basic_token):
    response = await client.post(
        "/api/v1/trends/",
        headers=auth_headers(basic_token),
        json={
            "name": "Unauthorized Trend",
            "category": "Style",
            "region": "Global",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_trend_admin(client: AsyncClient, admin_token, db_session):
    trend = await create_test_trend(db_session, name="Old Name")
    response = await client.patch(
        f"/api/v1/trends/{trend.id}",
        headers=auth_headers(admin_token),
        json={"trend_score": 99.0, "status": "peak"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["trend_score"] == 99.0
    assert data["status"] == "peak"


@pytest.mark.asyncio
async def test_delete_trend_admin(client: AsyncClient, admin_token, db_session):
    trend = await create_test_trend(db_session, name="To Delete")
    response = await client.delete(
        f"/api/v1/trends/{trend.id}",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 204

    # Confirm gone
    get_resp = await client.get(
        f"/api/v1/trends/{trend.id}",
        headers=auth_headers(admin_token),
    )
    assert get_resp.status_code == 404


# ── Dashboard ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard_summary(client: AsyncClient, basic_token, db_session):
    await create_test_trend(db_session, name="Dashboard T1")
    response = await client.get(
        "/api/v1/trends/dashboard",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_trends_tracked" in data
    assert "top_trends" in data
    assert "agent_status" in data
    assert "prediction_accuracy" in data
    assert isinstance(data["top_trends"], list)
