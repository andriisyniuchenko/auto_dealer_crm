from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_fail():
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong@test.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code in [400, 401]


def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "manager@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_current_user():
    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "manager@test.com",
            "password": "123456"
        }
    )

    token = login.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "manager@test.com"