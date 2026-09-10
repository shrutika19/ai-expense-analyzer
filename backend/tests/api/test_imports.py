from io import BytesIO

from fastapi.testclient import TestClient

from expense_analyzer.main import app
import json

client = TestClient(app)


def test_import_csv() -> None:
    csv_content = (
        "amount,description,category,expense_date\n"
        "100.00,Lunch,FOOD,2026-09-10\n"
        "250.00,Uber,TRANSPORT,2026-09-09\n"
    )

    response = client.post(
        "/api/v1/expenses/import",
        files={
            "file": (
                "expenses.csv",
                BytesIO(csv_content.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["imported_count"] == 2
    assert data["failed_count"] == 0


def test_import_json() -> None:
    json_content = json.dumps(
        [
            {
                "amount": "100.00",
                "description": "Lunch",
                "category": "FOOD",
                "expense_date": "2026-09-10",
            }
        ]
    )

    response = client.post(
        "/api/v1/expenses/import",
        files={
            "file": (
                "expenses.json",
                BytesIO(json_content.encode("utf-8")),
                "application/json",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["imported_count"] == 1



def test_import_unsupported_file() -> None:
    response = client.post(
        "/api/v1/expenses/import",
        files={
            "file": (
                "expenses.xml",
                BytesIO(b"<expenses />"),
                "application/xml",
            )
        },
    )

    assert response.status_code == 415

    data = response.json()

    assert data["error"]["code"] == (
        "UNSUPPORTED_FILE_TYPE"
    )