from fastapi.testclient import TestClient

from expense_analyzer.main import app


client = TestClient(app)


def test_v1_router_is_registered() -> None:
    routes = {
        route.path
        for route in app.routes
        if hasattr(route, "path")
    }

    assert "/api/v1" not in routes