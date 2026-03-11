import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def login(email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register_user(manager_token: str, role: str) -> tuple[str, str]:
    email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
    password = "123456"

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
    return email, password


def create_lead_as_user(token: str, first_name: str) -> int:
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


def test_salesperson_sees_only_own_leads():
    manager_token = login("manager@test.com", "123456")

    sales1_email, sales1_password = register_user(manager_token, "salesperson")
    sales2_email, sales2_password = register_user(manager_token, "salesperson")

    sales1_token = login(sales1_email, sales1_password)
    sales2_token = login(sales2_email, sales2_password)

    lead_id = create_lead_as_user(sales1_token, "LeadOwnedBySales1")

    sales1_leads = client.get(
        "/api/v1/leads/",
        headers=auth_headers(sales1_token),
    )
    assert sales1_leads.status_code == 200
    sales1_ids = [lead["id"] for lead in sales1_leads.json()]
    assert lead_id in sales1_ids

    sales2_leads = client.get(
        "/api/v1/leads/",
        headers=auth_headers(sales2_token),
    )
    assert sales2_leads.status_code == 200
    sales2_ids = [lead["id"] for lead in sales2_leads.json()]
    assert lead_id not in sales2_ids


def test_manager_sees_all_leads():
    manager_token = login("manager@test.com", "123456")

    sales_email, sales_password = register_user(manager_token, "salesperson")
    sales_token = login(sales_email, sales_password)

    lead_id = create_lead_as_user(sales_token, "ManagerCanSeeThis")

    response = client.get(
        "/api/v1/leads/",
        headers=auth_headers(manager_token),
    )
    assert response.status_code == 200

    ids = [lead["id"] for lead in response.json()]
    assert lead_id in ids


def test_manager_can_assign_second_salesperson_but_not_duplicate():
    manager_token = login("manager@test.com", "123456")

    sales1_email, sales1_password = register_user(manager_token, "salesperson")
    sales2_email, sales2_password = register_user(manager_token, "salesperson")

    sales1_token = login(sales1_email, sales1_password)

    lead_id = create_lead_as_user(sales1_token, "SharedLead")

    sales2_login = client.post(
        "/api/v1/auth/login",
        data={"username": sales2_email, "password": sales2_password},
    )
    sales2_id = sales2_login.json()["access_token"]  # temp to force login assertion
    assert sales2_login.status_code == 200

    me_response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers(sales2_login.json()["access_token"]),
    )
    assert me_response.status_code == 200
    sales2_user_id = me_response.json()["id"]

    assign_response = client.post(
        f"/api/v1/leads/{lead_id}/assign",
        json={"salesperson_id": sales2_user_id},
        headers=auth_headers(manager_token),
    )
    assert assign_response.status_code == 200

    duplicate_assign = client.post(
        f"/api/v1/leads/{lead_id}/assign",
        json={"salesperson_id": sales2_user_id},
        headers=auth_headers(manager_token),
    )
    assert duplicate_assign.status_code == 400