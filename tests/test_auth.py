import uuid


# ── login ───────────────────────────────────────────────────────────────────

def test_login_success(client, manager_user, manager_credentials):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": manager_credentials["email"], "password": manager_credentials["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client, manager_user, manager_credentials):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": manager_credentials["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@test.com", "password": "Test12345"},
    )
    assert response.status_code == 401


# ── register ─────────────────────────────────────────────────────────────────

def test_register_success(client, manager_token, auth_headers):
    email = f"new_{uuid.uuid4().hex[:8]}@test.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Test12345", "role": "salesperson"},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 200
    assert response.json()["email"] == email
    assert response.json()["role"] == "salesperson"


def test_register_weak_password_too_short(client, manager_token, auth_headers):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "weak@test.com", "password": "abc1", "role": "salesperson"},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 422


def test_register_weak_password_no_digit(client, manager_token, auth_headers):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "weak@test.com", "password": "onlyletters", "role": "salesperson"},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 422


def test_register_weak_password_no_letter(client, manager_token, auth_headers):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "weak@test.com", "password": "12345678", "role": "salesperson"},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 422


def test_register_duplicate_email(client, manager_token, auth_headers, manager_credentials):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": manager_credentials["email"], "password": "Test12345", "role": "salesperson"},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 409


def test_register_requires_auth(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@test.com", "password": "Test12345", "role": "salesperson"},
    )
    assert response.status_code == 401


def test_register_salesperson_cannot_register_others(client, salesperson_token, auth_headers):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@test.com", "password": "Test12345", "role": "salesperson"},
        headers=auth_headers(salesperson_token),
    )
    assert response.status_code == 403


# ── me ───────────────────────────────────────────────────────────────────────

def test_get_current_user(client, manager_token, auth_headers, manager_credentials):
    response = client.get("/api/v1/auth/me", headers=auth_headers(manager_token))
    assert response.status_code == 200
    assert response.json()["email"] == manager_credentials["email"]


def test_get_current_user_no_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == 401