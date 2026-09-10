from uuid import UUID

from fastapi.testclient import TestClient

from expense_analyzer.main import app


client = TestClient(app)


def test_create_expense() -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert UUID(data["id"])
    assert data == {
        "id": data["id"],
        "amount": "250.50",
        "description": "Lunch",
        "category": "Food",
        "expense_date": "2026-09-09",
    }




def test_create_expense_rejects_invalid_amount() -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "-100",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
    )

    assert response.status_code == 422




def test_create_expense_rejects_invalid_category() -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "description": "Lunch",
            "category": "InvalidCategory",
            "expense_date": "2026-09-09",
        },
    )

    assert response.status_code == 422




def test_create_expense_rejects_missing_description() -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
    )

    assert response.status_code == 422




def test_create_expense_rejects_extra_fields() -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
            "unexpected": "value",
        },
    )

    assert response.status_code == 422



def test_create_expense_persists_to_database() -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["amount"] == "250.50"
    assert data["description"] == "Lunch"
    assert data["category"] == "Food"
    assert data["expense_date"] == "2026-09-09"



def test_get_expenses() -> None:
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "500.00",
            "description": "Uber",
            "category": "Travel",
            "expense_date": "2026-09-08",
        },
    )

    assert create_response.status_code == 201

    created_expense = create_response.json()

    response = client.get("/api/v1/expenses")

    assert response.status_code == 200

    expenses = response.json()

    assert isinstance(expenses, list)

    matching_expense = next(
        expense
        for expense in expenses
        if expense["id"] == created_expense["id"]
    )

    assert matching_expense["amount"] == "500.00"
    assert matching_expense["description"] == "Uber"
    assert matching_expense["category"] == "Travel"
    assert matching_expense["expense_date"] == "2026-09-08"




def test_get_expenses_returns_list() -> None:
    response = client.get("/api/v1/expenses")

    assert response.status_code == 200
    assert isinstance(response.json(), list)