import pytest
import io

from app import create_app
from app.queueing.mm1 import MM1Queue
from app.queueing.mmc import MMCQueue
from app.models.simulation_customer import SimulationCustomer
from app.statistics.input_data import summarize_customers


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


# -------------------------
# M/M/1 model tests
# -------------------------

def test_mm1_calculates_correct_results():
    result = MM1Queue(4, 5).calculate()

    assert result["input"]["utilization"] == 0.8
    assert result["metrics"]["probability_empty"] == 0.2
    assert result["metrics"]["average_number_in_queue"] == 3.2
    assert result["metrics"]["average_number_in_system"] == 4.0
    assert result["metrics"]["average_waiting_time"] == 0.8
    assert result["metrics"]["average_system_time"] == 1.0


def test_mm1_rejects_unstable_system():
    with pytest.raises(ValueError):
        MM1Queue(5, 4)


# -------------------------
# M/M/c model tests
# -------------------------

def test_mmc_calculates_correct_results():
    result = MMCQueue(4, 5, 2).calculate()

    assert result["input"]["utilization"] == 0.4
    assert result["metrics"]["probability_empty"] == 0.428571
    assert result["metrics"]["probability_wait"] == 0.228571
    assert result["metrics"]["average_number_in_queue"] == 0.152381
    assert result["metrics"]["average_number_in_system"] == 0.952381
    assert result["metrics"]["average_waiting_time"] == 0.038095
    assert result["metrics"]["average_system_time"] == 0.238095


def test_mmc_rejects_unstable_system():
    with pytest.raises(ValueError):
        MMCQueue(11, 5, 2)


def test_mmc_rejects_zero_servers():
    with pytest.raises(ValueError):
        MMCQueue(4, 5, 0)


# -------------------------
# API endpoint tests
# -------------------------

def test_mm1_api_endpoint(client):
    response = client.post(
        "/api/queueing/mm1",
        json={
            "arrival_rate": 4,
            "service_rate": 5,
        },
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"


def test_mmc_api_endpoint(client):
    response = client.post(
        "/api/queueing/mmc",
        json={
            "arrival_rate": 4,
            "service_rate": 5,
            "server_count": 2,
        },
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"


def test_mm1_api_rejects_missing_input(client):
    response = client.post(
        "/api/queueing/mm1",
        json={
            "arrival_rate": 4,
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"
    
    
def test_custom_single_server_simulation(client):
    response = client.post(
        "/api/simulation/run",
        json={
            "simulation_type": "single_server",
            "customers": [
                {
                    "customer_id": "C1",
                    "arrival_time": 0,
                    "service_time": 5,
                },
                {
                    "customer_id": "C2",
                    "arrival_time": 2,
                    "service_time": 3,
                },
                {
                    "customer_id": "C3",
                    "arrival_time": 10,
                    "service_time": 4,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["simulation"]["customers_processed"] == 3

    customers = response.json["customers"]

    assert customers[0]["waiting_time"] == 0
    assert customers[1]["waiting_time"] == 3
    assert customers[2]["waiting_time"] == 0


def test_custom_multi_server_simulation(client):
    response = client.post(
        "/api/simulation/run",
        json={
            "simulation_type": "multi_server",
            "server_count": 2,
            "customers": [
                {
                    "customer_id": "C1",
                    "arrival_time": 0,
                    "service_time": 5,
                },
                {
                    "customer_id": "C2",
                    "arrival_time": 2,
                    "service_time": 3,
                },
                {
                    "customer_id": "C3",
                    "arrival_time": 3,
                    "service_time": 4,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["simulation"]["server_count"] == 2


def test_custom_simulation_rejects_empty_customers(client):
    response = client.post(
        "/api/simulation/run",
        json={
            "simulation_type": "single_server",
            "customers": [],
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_custom_simulation_rejects_negative_arrival_time(client):
    response = client.post(
        "/api/simulation/run",
        json={
            "simulation_type": "single_server",
            "customers": [
                {
                    "customer_id": "C1",
                    "arrival_time": -1,
                    "service_time": 5,
                },
            ],
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_custom_simulation_rejects_invalid_server_count(client):
    response = client.post(
        "/api/simulation/run",
        json={
            "simulation_type": "multi_server",
            "server_count": 0,
            "customers": [
                {
                    "customer_id": "C1",
                    "arrival_time": 0,
                    "service_time": 5,
                },
            ],
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"
    

def test_generated_simulation_endpoint(client):
    payload = {
        "simulation_type": "single_server",
        "customer_count": 10,
        "arrival_rate": 4,
        "service_rate": 5,
        "arrival_distribution": "exponential",
        "service_distribution": "exponential",
        "seed": 42,
    }

    response = client.post(
        "/api/simulation/generate-and-run",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["simulation"]["customers_processed"] == 10
    assert len(response.json["customers"]) == 10


def test_generated_simulation_rejects_invalid_distribution(client):
    response = client.post(
        "/api/simulation/generate-and-run",
        json={
            "simulation_type": "single_server",
            "customer_count": 10,
            "arrival_rate": 4,
            "service_rate": 5,
            "arrival_distribution": "invalid",
            "service_distribution": "exponential",
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_generated_simulation_rejects_zero_customer_count(client):
    response = client.post(
        "/api/simulation/generate-and-run",
        json={
            "simulation_type": "single_server",
            "customer_count": 0,
            "arrival_rate": 4,
            "service_rate": 5,
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"
    
    
def test_csv_upload_simulation(client):
    csv_content = (
        "customer_id,arrival_time,service_time\n"
        "C1,0,5\n"
        "C2,2,3\n"
        "C3,10,4\n"
    )

    response = client.post(
        "/api/simulation/upload-and-run",
        data={
            "file": (
                io.BytesIO(csv_content.encode("utf-8")),
                "customers.csv",
            ),
            "simulation_type": "single_server",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["simulation"]["customers_processed"] == 3
    assert len(response.json["customers"]) == 3


def test_csv_upload_rejects_missing_columns(client):
    csv_content = "customer_id,arrival_time\nC1,0\n"

    response = client.post(
        "/api/simulation/upload-and-run",
        data={
            "file": (
                io.BytesIO(csv_content.encode("utf-8")),
                "invalid.csv",
            ),
            "simulation_type": "single_server",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_upload_rejects_unsupported_file(client):
    response = client.post(
        "/api/simulation/upload-and-run",
        data={
            "file": (
                io.BytesIO(b"some content"),
                "customers.txt",
            ),
            "simulation_type": "single_server",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"
    
def test_input_data_statistics():
    customers = [
        SimulationCustomer("C1", 0, 5),
        SimulationCustomer("C2", 2, 3),
        SimulationCustomer("C3", 6, 4),
    ]

    result = summarize_customers(customers)

    assert result["customer_count"] == 3
    assert result["arrival_times"]["mean"] == 2.666667
    assert result["arrival_times"]["minimum"] == 0
    assert result["arrival_times"]["maximum"] == 6
    assert result["interarrival_times"]["mean"] == 3
    assert result["service_times"]["mean"] == 4
    assert result["estimated_arrival_rate"] == 0.333333
    assert result["estimated_service_rate"] == 0.25


def test_input_data_statistics_rejects_empty_customers():
    with pytest.raises(ValueError):
        summarize_customers([])
        
def test_uploaded_data_statistics(client):
    csv_content = (
        "customer_id,arrival_time,service_time\n"
        "C1,0,5\n"
        "C2,2,3\n"
        "C3,6,4\n"
    )

    response = client.post(
        "/api/statistics/describe-upload",
        data={
            "file": (
                io.BytesIO(csv_content.encode("utf-8")),
                "customers.csv",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"

    statistics = response.json["statistics"]

    assert statistics["customer_count"] == 3
    assert statistics["arrival_times"]["mean"] == 2.666667
    assert statistics["interarrival_times"]["mean"] == 3
    assert statistics["service_times"]["mean"] == 4


def test_uploaded_data_statistics_rejects_invalid_file(client):
    csv_content = "customer_id,arrival_time\nC1,0\n"

    response = client.post(
        "/api/statistics/describe-upload",
        data={
            "file": (
                io.BytesIO(csv_content.encode("utf-8")),
                "invalid.csv",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"
    

@pytest.mark.parametrize(
    "arrival_time,service_time",
    [
        ("invalid", 5),
        (0, "invalid"),
        (float("nan"), 5),
        (0, float("inf")),
        (float("-inf"), 5),
        (0, float("-inf")),
    ],
)
def test_custom_simulation_rejects_invalid_time_values(
    client,
    arrival_time,
    service_time,
):
    response = client.post(
        "/api/simulation/run",
        json={
            "simulation_type": "single_server",
            "customers": [
                {
                    "customer_id": "C1",
                    "arrival_time": arrival_time,
                    "service_time": service_time,
                },
            ],
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"
    

def test_upload_rejects_empty_csv(client):
    response = client.post(
        "/api/simulation/upload-and-run",
        data={
            "file": (
                io.BytesIO(b""),
                "empty.csv",
            ),
            "simulation_type": "single_server",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_upload_rejects_missing_file(client):
    response = client.post(
        "/api/simulation/upload-and-run",
        data={
            "simulation_type": "single_server",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


@pytest.mark.parametrize(
    "csv_content",
    [
        "arrival_time,service_time\n-1,5\n",
        "arrival_time,service_time\n0,0\n",
        "arrival_time,service_time\nNaN,5\n",
        "arrival_time,service_time\n0,inf\n",
        "arrival_time,service_time\nabc,5\n",
        "arrival_time,service_time\n0,\n",
    ],
)
def test_upload_rejects_invalid_time_values(
    client,
    csv_content,
):
    response = client.post(
        "/api/simulation/upload-and-run",
        data={
            "file": (
                io.BytesIO(csv_content.encode("utf-8")),
                "invalid_times.csv",
            ),
            "simulation_type": "single_server",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_upload_rejects_duplicate_customer_ids(client):
    csv_content = (
        "customer_id,arrival_time,service_time\n"
        "C1,0,5\n"
        "C1,2,3\n"
    )

    response = client.post(
        "/api/simulation/upload-and-run",
        data={
            "file": (
                io.BytesIO(csv_content.encode("utf-8")),
                "duplicate_ids.csv",
            ),
            "simulation_type": "single_server",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"