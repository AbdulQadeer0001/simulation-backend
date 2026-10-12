import pytest

from app.models.simulation_result import (
    CustomerSimulationResult,
    SimulationResult,
)
from app.services.result_formatter import ResultFormatter


@pytest.fixture
def sample_result():
    customer = CustomerSimulationResult(
        customer_id="C1",
        arrival_time=0.0,
        service_time=2.0,
        service_start=0.0,
        service_end=2.0,
        waiting_time=0.0,
        system_time=2.0,
        server_id=1,
        server_idle_time=0.0,
    )

    return SimulationResult(
        simulation_type="single_server",
        server_count=1,
        customers_processed=1,
        arrival_rate=0.5,
        service_rate=0.5,
        utilization=1.0,
        average_waiting_time=0.0,
        average_system_time=2.0,
        average_number_in_queue=0.0,
        average_number_in_system=1.0,
        throughput=0.5,
        total_idle_time=0.0,
        server_utilization={1: 1.0},
        customer_results=[customer],
    )


def test_customer_rows(sample_result):
    rows = ResultFormatter.customer_rows(sample_result)

    assert len(rows) == 1
    assert rows[0]["customer_id"] == "C1"
    assert rows[0]["waiting_time"] == 0.0
    assert rows[0]["server_id"] == 1
    assert rows[0]["simulation_type"] == "single_server"
    assert rows[0]["server_count"] == 1


def test_summary_rows(sample_result):
    rows = ResultFormatter.summary_rows(sample_result)

    assert len(rows) == 1
    assert rows[0]["customers_processed"] == 1
    assert rows[0]["average_waiting_time"] == 0.0
    assert rows[0]["server_utilization"] == {1: 1.0}
    assert "customer_results" not in rows[0]


def test_customer_rows_rejects_empty_customer_results(
    sample_result,
):
    sample_result.customer_results = []

    with pytest.raises(ValueError):
        ResultFormatter.customer_rows(sample_result)


def test_customer_rows_rejects_invalid_object():
    with pytest.raises(ValueError):
        ResultFormatter.customer_rows({})


def test_summary_rows_rejects_invalid_object():
    with pytest.raises(ValueError):
        ResultFormatter.summary_rows({})

