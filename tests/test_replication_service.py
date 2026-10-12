
import pytest

from app.services.replication_service import ReplicationService


def test_replications_return_summary_and_individual_results():
    result = ReplicationService.run_replications(
        simulation_type="single_server",
        customer_count=50,
        arrival_rate=0.5,
        service_rate=1.0,
        replication_count=5,
        seed=100,
    )

    assert result["simulation_type"] == "single_server"
    assert result["server_count"] == 1
    assert result["customer_count_per_replication"] == 50
    assert len(result["replications"]) == 5

    summary = result["summary"]

    assert summary["replication_count"] == 5
    assert "average_waiting_time" in summary["metrics"]
    assert (
        summary["metrics"]["average_waiting_time"]["confidence_interval"]
        is not None
    )


def test_replications_are_reproducible_with_same_seed():
    arguments = {
        "simulation_type": "single_server",
        "customer_count": 30,
        "arrival_rate": 0.5,
        "service_rate": 1.0,
        "replication_count": 3,
        "seed": 42,
    }

    first = ReplicationService.run_replications(**arguments)
    second = ReplicationService.run_replications(**arguments)

    assert first["replications"] == second["replications"]
    assert first["summary"] == second["summary"]


def test_multi_server_replications_use_requested_server_count():
    result = ReplicationService.run_replications(
        simulation_type="multi_server",
        customer_count=30,
        arrival_rate=0.5,
        service_rate=1.0,
        replication_count=3,
        server_count=2,
        seed=10,
    )

    assert result["server_count"] == 2
    assert len(result["replications"]) == 3


def test_invalid_replication_count_is_rejected():
    with pytest.raises(ValueError):
        ReplicationService.run_replications(
            simulation_type="single_server",
            customer_count=10,
            arrival_rate=0.5,
            service_rate=1.0,
            replication_count=1,
        )


def test_invalid_simulation_type_is_rejected():
    with pytest.raises(ValueError):
        ReplicationService.run_replications(
            simulation_type="invalid",
            customer_count=10,
            arrival_rate=0.5,
            service_rate=1.0,
            replication_count=3,
        )


def test_invalid_rate_is_rejected():
    with pytest.raises(ValueError):
        ReplicationService.run_replications(
            simulation_type="single_server",
            customer_count=10,
            arrival_rate=float("inf"),
            service_rate=1.0,
            replication_count=3,
        )
        


def test_invalid_confidence_level_is_rejected_before_simulation(
    monkeypatch,
):
    def simulation_should_not_run(*args, **kwargs):
        pytest.fail(
            "Simulation ran before confidence-level validation."
        )

    monkeypatch.setattr(
        "app.services.replication_service.SimulationService.run_single_server",
        simulation_should_not_run,
    )

    with pytest.raises(ValueError):
        ReplicationService.run_replications(
            simulation_type="single_server",
            customer_count=10,
            arrival_rate=0.5,
            service_rate=1.0,
            replication_count=3,
            confidence_level=1.0,
            seed=42,
        )