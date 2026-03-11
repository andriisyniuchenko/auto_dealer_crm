import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from app.main import app
from app.db.session import Base, get_db
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


TEST_DATABASE_URL = settings.TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)
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


@pytest.fixture
def manager_credentials():
    email = f"manager_{uuid.uuid4().hex[:8]}@test.com"
    password = "test123456"
    return {"email": email, "password": password}


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
        email="sales@test.com",
        hashed_password=hash_password("test123"),
        role="salesperson",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def manager_token(client, manager_user, manager_credentials):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": manager_credentials["email"],
            "password": manager_credentials["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def salesperson_token(client, salesperson_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "sales@test.com",
            "password": "test123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


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