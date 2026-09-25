from uuid import UUID


def test_create_expense(client, auth_headers) -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert UUID(data["id"])
    assert data["amount"] == "250.50"
    assert data["description"] == "Lunch"
    assert data["category"] == "Food"
    assert data["expense_date"] == "2026-09-09"
    assert data["category_source"] == "manual"
    assert data["predicted_category"] is not None
    assert data["category_confidence"] is not None
    assert data["model_version"] is not None


def test_create_expense_rejects_invalid_amount(
    client,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "-100",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_expense_rejects_invalid_category(
    client,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "description": "Lunch",
            "category": "InvalidCategory",
            "expense_date": "2026-09-09",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_expense_rejects_missing_description(
    client,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_expense_rejects_extra_fields(
    client,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
            "unexpected": "value",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_expense_persists_to_database(
    client,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["amount"] == "250.50"
    assert data["description"] == "Lunch"
    assert data["category"] == "Food"
    assert data["expense_date"] == "2026-09-09"
    assert data["category_source"] == "manual"
    assert data["predicted_category"] is not None
    assert data["category_confidence"] is not None
    assert data["model_version"] is not None


def test_get_expenses(client, auth_headers) -> None:
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "500.00",
            "description": "Uber",
            "category": "Travel",
            "expense_date": "2026-09-08",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    created_expense = create_response.json()

    response = client.get(
        "/api/v1/expenses",
        headers=auth_headers,
    )

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
    assert matching_expense["category_source"] == "manual"
    assert matching_expense["predicted_category"] is not None
    assert matching_expense["category_confidence"] is not None
    assert matching_expense["model_version"] is not None


def test_get_expenses_returns_list(
    client,
    auth_headers,
) -> None:
    response = client.get(
        "/api/v1/expenses",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

