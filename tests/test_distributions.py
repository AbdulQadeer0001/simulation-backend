
import math

import pytest

from app.simulation.distributions import DistributionGenerator


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf"), float("-inf"), True, "1"])
def test_exponential_interarrival_rejects_invalid_rates(rate):
    with pytest.raises(ValueError):
        DistributionGenerator.exponential_interarrival(rate)


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf"), float("-inf"), True, "1"])
def test_exponential_service_rejects_invalid_rates(rate):
    with pytest.raises(ValueError):
        DistributionGenerator.exponential_service(rate)


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf"), float("-inf"), True, "1"])
def test_deterministic_interarrival_rejects_invalid_rates(rate):
    with pytest.raises(ValueError):
        DistributionGenerator.deterministic_interarrival(rate)


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf"), float("-inf"), True, "1"])
def test_deterministic_service_rejects_invalid_rates(rate):
    with pytest.raises(ValueError):
        DistributionGenerator.deterministic_service(rate)


@pytest.mark.parametrize("seed", [True, 1.5, "42"])
def test_generate_customers_rejects_invalid_seed(seed):
    with pytest.raises(ValueError):
        DistributionGenerator.generate_customers(
            customer_count=5,
            arrival_rate=0.5,
            service_rate=1.0,
            seed=seed,
        )


@pytest.mark.parametrize(
    "arrival_rate,service_rate",
    [
        (float("nan"), 1.0),
        (float("inf"), 1.0),
        (0.5, float("nan")),
        (0.5, float("inf")),
    ],
)
def test_generate_customers_rejects_non_finite_rates(
    arrival_rate,
    service_rate,
):
    with pytest.raises(ValueError):
        DistributionGenerator.generate_customers(
            customer_count=5,
            arrival_rate=arrival_rate,
            service_rate=service_rate,
        )


def test_generate_customers_with_same_seed_is_reproducible():
    first = DistributionGenerator.generate_customers(
        customer_count=5,
        arrival_rate=0.5,
        service_rate=1.0,
        seed=42,
    )
    second = DistributionGenerator.generate_customers(
        customer_count=5,
        arrival_rate=0.5,
        service_rate=1.0,
        seed=42,
    )

    assert first == second


def test_deterministic_distributions_generate_expected_times():
    customers = DistributionGenerator.generate_customers(
        customer_count=3,
        arrival_rate=0.5,
        service_rate=2.0,
        arrival_distribution="deterministic",
        service_distribution="deterministic",
    )

    assert [c["arrival_time"] for c in customers] == [0.0, 2.0, 4.0]
    assert all(
        math.isclose(c["service_time"], 0.5)
        for c in customers
    )