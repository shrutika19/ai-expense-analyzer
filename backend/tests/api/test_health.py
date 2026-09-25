from fastapi.testclient import TestClient

from expense_analyzer.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "application": "AI Expense Analyzer",
        "version": "0.1.0",
    }


def test_ml_readiness_endpoint() -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["ml"]["model_version"] == "v1.0.0"
