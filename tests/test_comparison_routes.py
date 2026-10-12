import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_compare_endpoint_success(client):
    response = client.post(
        "/api/simulation/compare",
        json={
            "scenarios": [
                {
                    "name": "One counter",
                    "simulation_type": "multi_server",
                    "server_count": 1,
                    "customer_count": 30,
                    "arrival_rate": 0.5,
                    "service_rate": 1.0,
                    "replication_count": 3,
                    "seed": 42,
                },
                {
                    "name": "Two counters",
                    "simulation_type": "multi_server",
                    "server_count": 2,
                    "customer_count": 30,
                    "arrival_rate": 0.5,
                    "service_rate": 1.0,
                    "replication_count": 3,
                    "seed": 42,
                },
            ]
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["scenario_count"] == 2
    assert data["scenarios"][0]["scenario_name"] == "One counter"
    assert data["scenarios"][1]["server_count"] == 2
    assert "average_waiting_time" in (
        data["scenarios"][0]["metrics"]
    )


def test_compare_endpoint_rejects_empty_scenarios(client):
    response = client.post(
        "/api/simulation/compare",
        json={"scenarios": []},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_compare_endpoint_rejects_missing_scenarios(client):
    response = client.post(
        "/api/simulation/compare",
        json={},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_compare_endpoint_rejects_non_json_body(client):
    response = client.post(
        "/api/simulation/compare",
        data="not json",
        content_type="text/plain",
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_compare_endpoint_rejects_too_many_scenarios(client):
    response = client.post(
        "/api/simulation/compare",
        json={"scenarios": [{}] * 21},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()