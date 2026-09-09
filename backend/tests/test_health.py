from fastapi.testclient import TestClient

from expense_analyzer.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["application"] == "AI Expense Analyzer"
    assert data["version"] == "0.1.0"