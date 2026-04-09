import uuid


# ── create ───────────────────────────────────────────────────────────────────

def test_create_lead_success(client, salesperson_token, auth_headers):
    response = client.post(
        "/api/v1/leads/",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "phone": f"206{uuid.uuid4().hex[:7]}",
            "status": "active",
        },
        headers=auth_headers(salesperson_token),
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "John"


def test_create_lead_requires_auth(client):
    response = client.post(
        "/api/v1/leads/",
        json={"first_name": "John", "last_name": "Doe", "phone": "2060000001", "status": "active"},
    )
    assert response.status_code == 401


# ── list (paginated) ─────────────────────────────────────────────────────────

def test_get_leads_returns_paginated_response(client, salesperson_token, auth_headers, create_lead):
    create_lead(salesperson_token)
    response = client.get("/api/v1/leads/", headers=auth_headers(salesperson_token))
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert "limit" in data


def test_salesperson_sees_only_own_leads(client, register_user, login_user, auth_headers, create_lead):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, _ = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    s2_token = login_user(s2_email, s2_pass)

    lead_id = create_lead(s1_token, "OnlyForS1")

    s1_response = client.get("/api/v1/leads/", headers=auth_headers(s1_token))
    s2_response = client.get("/api/v1/leads/", headers=auth_headers(s2_token))

    assert s1_response.status_code == 200
    assert s2_response.status_code == 200

    s1_ids = [lead["id"] for lead in s1_response.json()["items"]]
    s2_ids = [lead["id"] for lead in s2_response.json()["items"]]

    assert lead_id in s1_ids
    assert lead_id not in s2_ids


def test_manager_sees_all_leads(client, manager_token, auth_headers, register_user, login_user, create_lead):
    s_email, s_pass, _ = register_user("salesperson")
    s_token = login_user(s_email, s_pass)
    lead_id = create_lead(s_token, "ManagerCanSee")

    response = client.get("/api/v1/leads/", headers=auth_headers(manager_token))
    assert response.status_code == 200

    ids = [lead["id"] for lead in response.json()["items"]]
    assert lead_id in ids


def test_get_leads_pagination_params(client, salesperson_token, auth_headers, create_lead):
    for i in range(3):
        create_lead(salesperson_token, f"Lead{i}")

    response = client.get("/api/v1/leads/?page=1&limit=2", headers=auth_headers(salesperson_token))
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2
    assert data["limit"] == 2


def test_get_leads_invalid_pagination(client, salesperson_token, auth_headers):
    response = client.get("/api/v1/leads/?page=0", headers=auth_headers(salesperson_token))
    assert response.status_code == 422


# ── update ───────────────────────────────────────────────────────────────────

def test_update_lead_success(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token, "BeforeUpdate")

    response = client.patch(
        f"/api/v1/leads/{lead_id}",
        json={"first_name": "AfterUpdate"},
        headers=auth_headers(salesperson_token),
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "AfterUpdate"


def test_salesperson_cannot_update_foreign_lead(
    client, register_user, login_user, auth_headers, create_lead
):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, _ = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    s2_token = login_user(s2_email, s2_pass)

    lead_id = create_lead(s1_token)

    response = client.patch(
        f"/api/v1/leads/{lead_id}",
        json={"first_name": "Hacked"},
        headers=auth_headers(s2_token),
    )
    assert response.status_code == 403


def test_update_lead_rejects_extra_fields(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token)
    response = client.patch(
        f"/api/v1/leads/{lead_id}",
        json={"first_name": "Valid", "id": 9999},
        headers=auth_headers(salesperson_token),
    )
    assert response.status_code == 422


# ── assign ───────────────────────────────────────────────────────────────────

def test_manager_can_assign_salesperson(
    client, manager_token, auth_headers, register_user, login_user, create_lead
):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, s2_id = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    lead_id = create_lead(s1_token)

    response = client.post(
        f"/api/v1/leads/{lead_id}/assign",
        json={"salesperson_id": s2_id},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 200


def test_salesperson_cannot_assign(client, register_user, login_user, auth_headers, create_lead):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, s2_id = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    lead_id = create_lead(s1_token)

    response = client.post(
        f"/api/v1/leads/{lead_id}/assign",
        json={"salesperson_id": s2_id},
        headers=auth_headers(s1_token),
    )
    assert response.status_code == 403


def test_cannot_assign_duplicate_salesperson(
    client, manager_token, auth_headers, register_user, login_user, create_lead
):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, s2_id = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    lead_id = create_lead(s1_token)

    client.post(
        f"/api/v1/leads/{lead_id}/assign",
        json={"salesperson_id": s2_id},
        headers=auth_headers(manager_token),
    )
    response = client.post(
        f"/api/v1/leads/{lead_id}/assign",
        json={"salesperson_id": s2_id},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 409


def test_cannot_assign_more_than_two_salespeople(
    client, manager_token, auth_headers, register_user, login_user, create_lead
):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, s2_id = register_user("salesperson")
    s3_email, s3_pass, s3_id = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    lead_id = create_lead(s1_token)

    client.post(
        f"/api/v1/leads/{lead_id}/assign",
        json={"salesperson_id": s2_id},
        headers=auth_headers(manager_token),
    )
    response = client.post(
        f"/api/v1/leads/{lead_id}/assign",
        json={"salesperson_id": s3_id},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 409