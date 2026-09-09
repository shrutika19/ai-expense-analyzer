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

    assert response.json() == {
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