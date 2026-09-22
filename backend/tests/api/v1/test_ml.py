def test_predict_category(
    client,
    auth_headers,
    monkeypatch,
) -> None:
    class FakePrediction:
        predicted_category = "Transport"
        confidence = 0.94

    class FakeInferenceService:
        def predict(self, prediction):
            return FakePrediction()

    from expense_analyzer.api.v1.dependencies import (
        get_inference_service,
    )
    from expense_analyzer.main import app

    app.dependency_overrides[
        get_inference_service
    ] = lambda: FakeInferenceService()

    try:
        response = client.post(
            "/api/v1/ml/predict-category",
            json={
                "description": "Uber ride to office",
                "amount": 250,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json() == {
            "predicted_category": "Transport",
            "confidence": 0.94,
        }
    finally:
        app.dependency_overrides.pop(
            get_inference_service,
            None,
        )


def test_predict_category_requires_authentication(
    client,
) -> None:
    response = client.post(
        "/api/v1/ml/predict-category",
        json={
            "description": "Uber ride to office",
            "amount": 250,
        },
    )

    assert response.status_code == 401


def test_predict_category_rejects_empty_description(
    client,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/ml/predict-category",
        json={
            "description": "",
            "amount": 250.0,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_predict_category_rejects_description_over_500_characters(
    client,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/ml/predict-category",
        json={
            "description": "A" * 501,
            "amount": 250,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_predict_category_rejects_non_positive_amount(
    client,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/ml/predict-category",
        json={
            "description": "Uber ride",
            "amount": -180,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422