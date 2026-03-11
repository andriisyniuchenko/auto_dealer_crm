def test_salesperson_cannot_create_deal_for_foreign_lead(
    client,
    register_user,
    login_user,
    auth_headers,
    create_lead,
):
    sales1_email, sales1_password, _ = register_user("salesperson")
    sales2_email, sales2_password, _ = register_user("salesperson")

    sales1_token = login_user(sales1_email, sales1_password)
    sales2_token = login_user(sales2_email, sales2_password)

    lead_id = create_lead(sales1_token, "ForeignLead")

    response = client.post(
        "/api/v1/deals/",
        json={
            "lead_id": lead_id,
            "vehicle": "Subaru Crosstrek",
            "price": 28000,
        },
        headers=auth_headers(sales2_token),
    )

    assert response.status_code == 403


def test_cannot_create_duplicate_deal_for_same_lead(
    client,
    register_user,
    login_user,
    auth_headers,
    create_lead,
):
    sales_email, sales_password, _ = register_user("salesperson")
    sales_token = login_user(sales_email, sales_password)

    lead_id = create_lead(sales_token, "DuplicateDealLead")

    first_deal = client.post(
        "/api/v1/deals/",
        json={
            "lead_id": lead_id,
            "vehicle": "Subaru Outback",
            "price": 32000,
        },
        headers=auth_headers(sales_token),
    )

    assert first_deal.status_code == 200

    duplicate_deal = client.post(
        "/api/v1/deals/",
        json={
            "lead_id": lead_id,
            "vehicle": "Subaru Outback",
            "price": 32000,
        },
        headers=auth_headers(sales_token),
    )

    assert duplicate_deal.status_code == 400


def test_shared_deal_counts_as_half_for_each_salesperson(
    client,
    manager_token,
    auth_headers,
    register_user,
    login_user,
    create_lead,
):
    sales1_email, sales1_password, _ = register_user("salesperson")
    sales2_email, sales2_password, sales2_user_id = register_user("salesperson")

    sales1_token = login_user(sales1_email, sales1_password)

    lead_id = create_lead(sales1_token, "SharedDealLead")

    assign_response = client.post(
        f"/api/v1/leads/{lead_id}/assign",
        json={"salesperson_id": sales2_user_id},
        headers=auth_headers(manager_token),
    )

    assert assign_response.status_code == 200

    deal_response = client.post(
        "/api/v1/deals/",
        json={
            "lead_id": lead_id,
            "vehicle": "Toyota Camry",
            "price": 25000,
        },
        headers=auth_headers(sales1_token),
    )

    assert deal_response.status_code == 200
    deal_id = deal_response.json()["id"]

    close_response = client.patch(
        f"/api/v1/deals/{deal_id}/close",
        json={"status": "sold"},
        headers=auth_headers(sales1_token),
    )

    assert close_response.status_code == 200

    stats_response = client.get(
        "/api/v1/stats/sales",
        headers=auth_headers(manager_token),
    )

    assert stats_response.status_code == 200

    stats = stats_response.json()

    sales1_stat = next(item for item in stats if item["email"] == sales1_email)
    sales2_stat = next(item for item in stats if item["email"] == sales2_email)

    assert sales1_stat["sold_count"] == 0.5
    assert sales2_stat["sold_count"] == 0.5