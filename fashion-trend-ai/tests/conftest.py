"""
pytest configuration and shared fixtures.
Uses an in-memory SQLite database for fast isolated tests.
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.db.base import Base, get_db
from app.db.models.models import User, SubscriptionPlan, Subscription
from app.core.security import hash_password, create_access_token


# ── Event Loop ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── In-memory test DB ─────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncSession:
    session_factory = async_sessionmaker(
        bind=test_engine, expire_on_commit=False, autoflush=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


# ── App with overridden DB ─────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def app(db_session):
    fastapi_app = create_app()

    async def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    return fastapi_app


@pytest_asyncio.fixture
async def client(app) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Test Users ─────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def basic_user(db_session) -> User:
    user = User(
        name="Basic User",
        email="basic@test.com",
        password_hash=hash_password("password123"),
        role="boutique_owner",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def pro_user(db_session) -> User:
    user = User(
        name="Pro User",
        email="pro@test.com",
        password_hash=hash_password("password123"),
        role="boutique_owner",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    # Create Pro plan and subscription
    plan = SubscriptionPlan(
        name="Pro",
        type="monthly",
        price=149.00,
        features={"predictions": True, "ai_recommendations": True},
    )
    db_session.add(plan)
    await db_session.flush()

    sub = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        status="active",
    )
    db_session.add(sub)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def admin_user(db_session) -> User:
    user = User(
        name="Admin",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


# ── Auth Helpers ──────────────────────────────────────────────────────────────

@pytest.fixture
def basic_token(basic_user) -> str:
    return create_access_token(basic_user.id)


@pytest.fixture
def pro_token(pro_user) -> str:
    return create_access_token(pro_user.id)


@pytest.fixture
def admin_token(admin_user) -> str:
    return create_access_token(admin_user.id)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
