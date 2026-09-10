from decimal import Decimal

from fastapi.testclient import TestClient

from expense_analyzer.main import app


client = TestClient(app)


def test_get_summary() -> None:
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "100.00",
            "description": "Food",
            "category": "FOOD",
            "expense_date": "2026-01-10",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/analytics/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_amount" in data
    assert "expense_count" in data
    assert "average_amount" in data
    assert "highest_amount" in data
    assert "lowest_amount" in data


def test_get_category_summary() -> None:
    response = client.get(
        "/api/v1/analytics/categories"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        assert "category" in data[0]
        assert "total_amount" in data[0]
        assert "expense_count" in data[0]


def test_get_monthly_summary() -> None:
    response = client.get(
        "/api/v1/analytics/monthly"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        assert "month" in data[0]
        assert "total_amount" in data[0]
        assert "expense_count" in data[0]



def test_get_summary_returns_correct_values() -> None:
    client.post(
        "/api/v1/expenses",
        json={
            "amount": "100.00",
            "description": "Food",
            "category": "FOOD",
            "expense_date": "2026-03-10",
        },
    )

    client.post(
        "/api/v1/expenses",
        json={
            "amount": "300.00",
            "description": "Transport",
            "category": "TRANSPORT",
            "expense_date": "2026-03-15",
        },
    )

    response = client.get(
        "/api/v1/analytics/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_amount"]) >= Decimal("400.00")
    assert data["expense_count"] >= 2