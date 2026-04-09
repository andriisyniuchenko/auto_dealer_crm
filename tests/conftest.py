import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import Base, get_db
from app.main import app
from app.models.user import User

engine = create_engine(settings.TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── users ──────────────────────────────────────────────────────────────────

@pytest.fixture
def manager_credentials():
    return {"email": f"manager_{uuid.uuid4().hex[:8]}@test.com", "password": "Test12345"}


@pytest.fixture
def manager_user(db, manager_credentials):
    user = User(
        email=manager_credentials["email"],
        hashed_password=hash_password(manager_credentials["password"]),
        role="manager",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def salesperson_user(db):
    user = User(
        email=f"sales_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password=hash_password("Test12345"),
        role="salesperson",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── tokens ─────────────────────────────────────────────────────────────────

@pytest.fixture
def manager_token(client, manager_user, manager_credentials):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": manager_credentials["email"], "password": manager_credentials["password"]},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def salesperson_token(client, salesperson_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": salesperson_user.email, "password": "Test12345"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# ── helpers ─────────────────────────────────────────────────────────────────

@pytest.fixture
def auth_headers():
    def _make(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
    return _make


@pytest.fixture
def register_user(client, manager_token, auth_headers):
    """Register a user via API. Returns (email, password, user_id)."""
    def _register(role: str):
        email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
        password = "Test12345"
        response = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "role": role},
            headers=auth_headers(manager_token),
        )
        assert response.status_code == 200, response.json()
        return email, password, response.json()["id"]
    return _register


@pytest.fixture
def login_user(client):
    """Login and return access token."""
    def _login(email: str, password: str) -> str:
        response = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        assert response.status_code == 200, response.json()
        return response.json()["access_token"]
    return _login


@pytest.fixture
def create_lead(client, auth_headers):
    """Create a lead and return its id."""
    def _create(token: str, first_name: str = "Test") -> int:
        response = client.post(
            "/api/v1/leads/",
            json={
                "first_name": first_name,
                "last_name": "Lead",
                "phone": f"206{uuid.uuid4().hex[:7]}",
                "email": f"{uuid.uuid4().hex[:8]}@lead.com",
                "city": "Seattle",
                "state": "WA",
                "source": "test",
                "interest": "Subaru Crosstrek",
                "status": "active",
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 200, response.json()
        return response.json()["id"]
    return _create