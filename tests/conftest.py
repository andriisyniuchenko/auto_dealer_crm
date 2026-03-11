import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def manager_credentials():
    email = f"manager_{uuid.uuid4().hex[:8]}@test.com"
    password = "test123456"
    return {"email": email, "password": password}


@pytest.fixture
def manager_token(client, manager_credentials):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == manager_credentials["email"]).first()
        if not existing:
            manager = User(
                email=manager_credentials["email"],
                hashed_password=hash_password(manager_credentials["password"]),
                role="general_manager",
                is_active=True,
            )
            db.add(manager)
            db.commit()
    finally:
        db.close()

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": manager_credentials["email"],
            "password": manager_credentials["password"],
        },
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


@pytest.fixture
def auth_headers():
    def _auth_headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
    return _auth_headers


@pytest.fixture
def register_user(client, manager_token, auth_headers):
    def _register_user(role: str):
        email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
        password = "test123456"

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "role": role,
            },
            headers=auth_headers(manager_token),
        )
        assert response.status_code == 200
        return email, password, response.json()["id"]

    return _register_user


@pytest.fixture
def login_user(client):
    def _login_user(email: str, password: str) -> str:
        response = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        assert response.status_code == 200
        return response.json()["access_token"]

    return _login_user


@pytest.fixture
def create_lead(client, auth_headers):
    def _create_lead(token: str, first_name: str):
        response = client.post(
            "/api/v1/leads/",
            json={
                "first_name": first_name,
                "last_name": "Test",
                "phone": f"206{uuid.uuid4().hex[:7]}",
                "email": f"{uuid.uuid4().hex[:8]}@lead.com",
                "city": "Seattle",
                "state": "WA",
                "source": "test",
                "interest": "Subaru Crosstrek",
                "notes": "pytest lead",
                "status": "active",
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        return response.json()["id"]

    return _create_lead