
import pytest

from app.services.comparison_service import ComparisonService


def test_compare_two_scenarios():
    result = ComparisonService.compare_scenarios([
        {
            "name": "One counter",
            "simulation_type": "multi_server",
            "server_count": 1,
            "customer_count": 30,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "replication_count": 3,
        },
        {
            "name": "Two counters",
            "simulation_type": "multi_server",
            "server_count": 2,
            "customer_count": 30,
            "arrival_rate": 0.5,
            "service_rate": 1.0,
            "replication_count": 3,
        },
    ])

    assert result["scenario_count"] == 2
    assert result["scenarios"][0]["scenario_name"] == "One counter"
    assert result["scenarios"][1]["server_count"] == 2
    assert "average_waiting_time" in result["scenarios"][0]["metrics"]


def test_compare_rejects_empty_scenarios():
    with pytest.raises(ValueError):
        ComparisonService.compare_scenarios([])


def test_compare_rejects_more_than_twenty_scenarios():
    with pytest.raises(ValueError):
        ComparisonService.compare_scenarios([{}] * 21)


def test_compare_rejects_non_object_scenario():
    with pytest.raises(ValueError):
        ComparisonService.compare_scenarios(["invalid"])
        

@pytest.mark.parametrize(
    "invalid_name",
    [None, 123, "", "   "],
)
def test_compare_rejects_invalid_scenario_name(invalid_name):
    with pytest.raises(ValueError, match="name must be"):
        ComparisonService.compare_scenarios([
            {
                "name": invalid_name,
            }
        ])

