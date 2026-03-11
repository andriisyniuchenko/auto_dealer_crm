def test_login_fail(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_success(client, manager_credentials, manager_token):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": manager_credentials["email"],
            "password": manager_credentials["password"],
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_current_user(client, manager_token, auth_headers, manager_credentials):
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 200
    assert response.json()["email"] == manager_credentials["email"]