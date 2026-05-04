"""API smoke tests for the prototype backend."""

from fastapi.testclient import TestClient

from api.main import create_app


client = TestClient(create_app())


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_endpoint() -> None:
    response = client.post(
        "/predict",
        json={
            "age_group": "Above45",
            "gender": "Female",
            "hiv_status": "Positive",
            "registration_group": "Relapse",
            "drtb_type": "RR-TB",
            "district": "Kabwe",
            "year_of_diagnosis": 2021,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert body["predicted_outcome"] in body["probabilities"]
    assert body["explanation"]
    assert body["model_version"] == "logistic-reconstruction-v1"


def test_predict_rejects_unknown_fields() -> None:
    response = client.post(
        "/predict",
        json={
            "age_group": "Above45",
            "gender": "Female",
            "hiv_status": "Positive",
            "registration_group": "Relapse",
            "drtb_type": "RR-TB",
            "district": "Kabwe",
            "patient_name": "Do not accept identifiers",
        },
    )

    assert response.status_code == 422
