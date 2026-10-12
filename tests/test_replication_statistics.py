
import pytest

from app.statistics.replication_statistics import (
    ReplicationStatistics,
)


def test_summarize_calculates_mean_and_confidence_interval():
    result = ReplicationStatistics.summarize(
        [4, 5, 6, 4, 6]
    )

    assert result["replication_count"] == 5
    assert result["mean"] == 5
    assert result["standard_deviation"] == pytest.approx(
        1.0
    )
    assert result["confidence_interval"]["lower"] < 5
    assert result["confidence_interval"]["upper"] > 5


def test_single_replication_has_no_confidence_interval():
    result = ReplicationStatistics.summarize([5])

    assert result["mean"] == 5
    assert result["standard_deviation"] is None
    assert result["confidence_interval"] is None


def test_invalid_confidence_level_is_rejected():
    with pytest.raises(ValueError):
        ReplicationStatistics.summarize(
            [4, 5, 6],
            confidence_level=1.0,
        )


def test_empty_values_are_rejected():
    with pytest.raises(ValueError):
        ReplicationStatistics.summarize([])


def test_non_numeric_values_are_rejected():
    with pytest.raises(ValueError):
        ReplicationStatistics.summarize([4, "invalid", 6])


def test_non_finite_values_are_rejected():
    with pytest.raises(ValueError):
        ReplicationStatistics.summarize([4, float("inf")])
        

def test_string_confidence_level_raises_value_error():
    with pytest.raises(ValueError):
        ReplicationStatistics.summarize(
            [4, 5, 6],
            confidence_level="0.95",
        )