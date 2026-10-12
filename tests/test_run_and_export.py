import io
import pytest
from openpyxl import load_workbook

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_run_and_export_csv_returns_download(client):
    response = client.post(
        "/api/simulation/run-and-export/csv",
        json={
            "simulation_type": "single_server",
            "customer_count": 10,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "seed": 42,
        },
    )

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment;" in response.headers["Content-Disposition"]
    assert b"customer_id" in response.data
    assert b"C1" in response.data


def test_run_and_export_excel_returns_download(client):
    response = client.post(
        "/api/simulation/run-and-export/excel",
        json={
            "simulation_type": "single_server",
            "customer_count": 10,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "seed": 42,
        },
    )

    assert response.status_code == 200
    assert "spreadsheetml.sheet" in response.mimetype
    assert "attachment;" in response.headers["Content-Disposition"]

    workbook = load_workbook(io.BytesIO(response.data))
    worksheet = workbook.active

    assert worksheet.title == "Customer Results"
    assert "customer_id" in [
        cell.value for cell in worksheet[1]
    ]


def test_run_and_export_csv_summary(client):
    response = client.post(
        "/api/simulation/run-and-export/csv",
        json={
            "simulation_type": "single_server",
            "customer_count": 10,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "seed": 42,
            "export_type": "summary",
        },
    )

    assert response.status_code == 200
    assert b"average_waiting_time" in response.data
    assert b"customers_processed" in response.data


def test_run_and_export_rejects_invalid_simulation_type(client):
    response = client.post(
        "/api/simulation/run-and-export/csv",
        json={
            "simulation_type": "invalid",
            "customer_count": 10,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_run_and_export_rejects_invalid_export_type(client):
    response = client.post(
        "/api/simulation/run-and-export/excel",
        json={
            "simulation_type": "single_server",
            "customer_count": 10,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "seed": 42,
            "export_type": "invalid",
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_run_and_export_rejects_non_object_json(client):
    response = client.post(
        "/api/simulation/run-and-export/csv",
        json=["invalid"],
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"
    

@pytest.mark.parametrize(
    "field,value",
    [
        ("customer_count", 0),
        ("customer_count", -1),
        ("customer_count", 1.5),
        ("arrival_rate", 0),
        ("arrival_rate", -1),
        ("service_rate", 0),
        ("service_rate", -1),
        ("server_count", 0),
    ],
)
def test_run_and_export_rejects_invalid_numeric_inputs(
    client,
    field,
    value,
):
    payload = {
        "simulation_type": "multi_server",
        "customer_count": 10,
        "arrival_rate": 0.5,
        "service_rate": 1.0,
        "server_count": 2,
        "seed": 42,
    }
    payload[field] = value

    response = client.post(
        "/api/simulation/run-and-export/csv",
        json=payload,
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"