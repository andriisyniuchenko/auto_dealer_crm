from datetime import datetime, timedelta, timezone


def _future_dt():
    return (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()


def _create_appointment(client, token, lead_id, headers):
    return client.post(
        f"/api/v1/leads/{lead_id}/appointments/",
        json={"appointment_at": _future_dt(), "status": "scheduled"},
        headers=headers,
    )


# ── create ───────────────────────────────────────────────────────────────────

def test_create_appointment_success(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token)
    response = _create_appointment(client, salesperson_token, lead_id, auth_headers(salesperson_token))
    assert response.status_code == 200
    assert response.json()["status"] == "scheduled"
    assert response.json()["lead_id"] == lead_id


def test_create_appointment_requires_auth(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token)
    response = client.post(
        f"/api/v1/leads/{lead_id}/appointments/",
        json={"appointment_at": _future_dt(), "status": "scheduled"},
    )
    assert response.status_code == 401


def test_cannot_create_appointment_for_foreign_lead(
    client, register_user, login_user, auth_headers, create_lead
):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, _ = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    s2_token = login_user(s2_email, s2_pass)

    lead_id = create_lead(s1_token)
    response = _create_appointment(client, s2_token, lead_id, auth_headers(s2_token))
    assert response.status_code == 403


# ── list (paginated) ─────────────────────────────────────────────────────────

def test_get_appointments_returns_paginated_response(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token)
    _create_appointment(client, salesperson_token, lead_id, auth_headers(salesperson_token))

    response = client.get(
        f"/api/v1/leads/{lead_id}/appointments/",
        headers=auth_headers(salesperson_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1


# ── update ───────────────────────────────────────────────────────────────────

def test_update_appointment_status(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token)
    headers = auth_headers(salesperson_token)
    appointment_id = _create_appointment(client, salesperson_token, lead_id, headers).json()["id"]

    response = client.patch(
        f"/api/v1/leads/{lead_id}/appointments/{appointment_id}",
        json={"status": "confirmed"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_salesperson_cannot_update_foreign_appointment(
    client, manager_token, auth_headers, register_user, login_user, create_lead
):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, _ = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    s2_token = login_user(s2_email, s2_pass)

    lead_id = create_lead(s1_token)
    headers_s1 = auth_headers(s1_token)
    appointment_id = _create_appointment(client, s1_token, lead_id, headers_s1).json()["id"]

    response = client.patch(
        f"/api/v1/leads/{lead_id}/appointments/{appointment_id}",
        json={"status": "confirmed"},
        headers=auth_headers(s2_token),
    )
    assert response.status_code == 403


def test_cannot_update_appointment_with_wrong_lead_id(
    client, salesperson_token, auth_headers, create_lead
):
    headers = auth_headers(salesperson_token)
    lead_id = create_lead(salesperson_token)
    other_lead_id = create_lead(salesperson_token)
    appointment_id = _create_appointment(client, salesperson_token, lead_id, headers).json()["id"]

    response = client.patch(
        f"/api/v1/leads/{other_lead_id}/appointments/{appointment_id}",
        json={"status": "confirmed"},
        headers=headers,
    )
    assert response.status_code == 404


def test_manager_can_update_any_appointment(
    client, manager_token, auth_headers, register_user, login_user, create_lead
):
    s_email, s_pass, _ = register_user("salesperson")
    s_token = login_user(s_email, s_pass)

    lead_id = create_lead(s_token)
    appointment_id = _create_appointment(
        client, s_token, lead_id, auth_headers(s_token)
    ).json()["id"]

    response = client.patch(
        f"/api/v1/leads/{lead_id}/appointments/{appointment_id}",
        json={"status": "confirmed"},
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 200