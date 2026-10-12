import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_replication_endpoint_success(client):
    response = client.post(
        "/api/simulation/replicate",
        json={
            "simulation_type": "single_server",
            "customer_count": 30,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "replication_count": 3,
            "seed": 42,
            "confidence_level": 0.95,
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["simulation_type"] == "single_server"
    assert data["server_count"] == 1
    assert len(data["replications"]) == 3
    assert data["summary"]["replication_count"] == 3
    assert "average_waiting_time" in data["summary"]["metrics"]


def test_replication_endpoint_rejects_invalid_simulation_type(client):
    response = client.post(
        "/api/simulation/replicate",
        json={
            "simulation_type": "invalid",
            "customer_count": 30,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "replication_count": 3,
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_replication_endpoint_rejects_invalid_replication_count(client):
    response = client.post(
        "/api/simulation/replicate",
        json={
            "simulation_type": "single_server",
            "customer_count": 30,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "replication_count": 1,
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_replication_endpoint_multi_server(client):
    response = client.post(
        "/api/simulation/replicate",
        json={
            "simulation_type": "multi_server",
            "customer_count": 30,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "replication_count": 3,
            "server_count": 2,
            "seed": 42,
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["simulation_type"] == "multi_server"
    assert data["server_count"] == 2
    assert len(data["replications"]) == 3


def test_replication_endpoint_rejects_non_json_body(client):
    response = client.post(
        "/api/simulation/replicate",
        data="not json",
        content_type="text/plain",
    )

    assert response.status_code == 400
    assert "error" in response.get_json()

