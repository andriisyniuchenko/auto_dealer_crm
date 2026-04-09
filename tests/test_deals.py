def _create_deal(client, token, lead_id, headers, vehicle="Subaru Outback", price=32000):
    return client.post(
        "/api/v1/deals/",
        json={"lead_id": lead_id, "vehicle": vehicle, "price": price},
        headers=headers,
    )


# ── create ───────────────────────────────────────────────────────────────────

def test_create_deal_success(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token)
    response = _create_deal(client, salesperson_token, lead_id, auth_headers(salesperson_token))
    assert response.status_code == 200
    assert response.json()["vehicle"] == "Subaru Outback"
    assert response.json()["status"] == "open"


def test_create_deal_for_nonexistent_lead(client, salesperson_token, auth_headers):
    response = _create_deal(client, salesperson_token, 999999, auth_headers(salesperson_token))
    assert response.status_code == 404


def test_salesperson_cannot_create_deal_for_foreign_lead(
    client, register_user, login_user, auth_headers, create_lead
):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, _ = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    s2_token = login_user(s2_email, s2_pass)

    lead_id = create_lead(s1_token)
    response = _create_deal(client, s2_token, lead_id, auth_headers(s2_token))
    assert response.status_code == 403


def test_cannot_create_duplicate_deal(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token)
    headers = auth_headers(salesperson_token)

    _create_deal(client, salesperson_token, lead_id, headers)
    response = _create_deal(client, salesperson_token, lead_id, headers)
    assert response.status_code == 409


# ── close ─────────────────────────────────────────────────────────────────────

def test_close_deal_as_sold(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token)
    headers = auth_headers(salesperson_token)

    deal_id = _create_deal(client, salesperson_token, lead_id, headers).json()["id"]

    response = client.patch(
        f"/api/v1/deals/{deal_id}/close",
        json={"status": "sold"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "sold"


def test_cannot_close_already_closed_deal(client, salesperson_token, auth_headers, create_lead):
    lead_id = create_lead(salesperson_token)
    headers = auth_headers(salesperson_token)

    deal_id = _create_deal(client, salesperson_token, lead_id, headers).json()["id"]
    client.patch(f"/api/v1/deals/{deal_id}/close", json={"status": "sold"}, headers=headers)

    response = client.patch(
        f"/api/v1/deals/{deal_id}/close",
        json={"status": "lost"},
        headers=headers,
    )
    assert response.status_code == 400


def test_salesperson_cannot_close_foreign_deal(
    client, register_user, login_user, auth_headers, create_lead
):
    s1_email, s1_pass, _ = register_user("salesperson")
    s2_email, s2_pass, _ = register_user("salesperson")

    s1_token = login_user(s1_email, s1_pass)
    s2_token = login_user(s2_email, s2_pass)

    lead_id = create_lead(s1_token)
    deal_id = _create_deal(client, s1_token, lead_id, auth_headers(s1_token)).json()["id"]

    response = client.patch(
        f"/api/v1/deals/{deal_id}/close",
        json={"status": "sold"},
        headers=auth_headers(s2_token),
    )
    assert response.status_code == 403


# ── stats — shared 50/50 ─────────────────────────────────────────────────────

def test_shared_deal_counts_as_half(
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

    deal_id = _create_deal(client, s1_token, lead_id, auth_headers(s1_token)).json()["id"]
    client.patch(f"/api/v1/deals/{deal_id}/close", json={"status": "sold"}, headers=auth_headers(s1_token))

    stats = client.get("/api/v1/stats/sales", headers=auth_headers(manager_token)).json()

    s1_stat = next(s for s in stats if s["email"] == s1_email)
    s2_stat = next(s for s in stats if s["email"] == s2_email)

    assert s1_stat["sold_count"] == 0.5
    assert s2_stat["sold_count"] == 0.5


def test_sole_deal_counts_as_one(client, auth_headers, register_user, login_user, create_lead, manager_token):
    s_email, s_pass, _ = register_user("salesperson")
    s_token = login_user(s_email, s_pass)

    lead_id = create_lead(s_token)
    deal_id = _create_deal(client, s_token, lead_id, auth_headers(s_token)).json()["id"]
    client.patch(f"/api/v1/deals/{deal_id}/close", json={"status": "sold"}, headers=auth_headers(s_token))

    stats = client.get("/api/v1/stats/sales", headers=auth_headers(manager_token)).json()
    s_stat = next(s for s in stats if s["email"] == s_email)
    assert s_stat["sold_count"] == 1.0