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


def test_import_rejects_mismatched_mime_type() -> None:
    response = client.post(
        "/api/v1/expenses/import",
        files={
            "file": (
                "expenses.csv",
                BytesIO(b"amount,description,category,expense_date\n"),
                "application/json",
            )
        },
    )

    assert response.status_code == 415
    assert response.json()["detail"]["code"] == (
        "UNSUPPORTED_MEDIA_TYPE"
    )


def test_import_rejects_oversized_file() -> None:
    oversized_content = b"a" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/api/v1/expenses/import",
        files={
            "file": (
                "expenses.csv",
                BytesIO(oversized_content),
                "text/csv",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "FILE_TOO_LARGE"


def test_import_rejects_malformed_json() -> None:
    response = client.post(
        "/api/v1/expenses/import",
        files={
            "file": (
                "expenses.json",
                BytesIO(b"[{invalid json"),
                "application/json",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"].startswith(
        "Invalid expense import data:"
    )


def test_import_rejects_csv_with_missing_columns() -> None:
    response = client.post(
        "/api/v1/expenses/import",
        files={
            "file": (
                "expenses.csv",
                BytesIO(b"amount,description\n100.00,Lunch\n"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 422
    assert "missing required columns" in response.json()["detail"]


def test_import_reports_invalid_rows_and_saves_valid_rows() -> None:
    csv_content = (
        "amount,description,category,expense_date\n"
        "100.00,Lunch,FOOD,2026-09-10\n"
        "not-a-number,Invalid,FOOD,2026-09-10\n"
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
    assert data["imported_count"] == 1
    assert data["failed_count"] == 1
    assert data["errors"] == [
        {
            "row_number": 3,
            "reason": "Invalid expense amount: not-a-number",
        }
    ]


def test_import_skips_and_reports_duplicates() -> None:
    csv_content = (
        "amount,description,category,expense_date\n"
        "100.00,Lunch,FOOD,2026-09-10\n"
        "100.00,Lunch,FOOD,2026-09-10\n"
    )

    response = client.post(
        "/api/v1/expenses/import",
        files={
            "file": (
                "duplicates.csv",
                BytesIO(csv_content.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["imported_count"] == 1
    assert data["failed_count"] == 0
    assert data["duplicate_count"] == 1
    assert data["skipped_rows"] == [
        {
            "row_number": 3,
            "reason": "Duplicate expense skipped.",
        }
    ]