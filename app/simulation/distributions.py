
import math
import random


class DistributionGenerator:

    @staticmethod
    def _validate_rate(rate, name):
        if (
            isinstance(rate, bool)
            or not isinstance(rate, (int, float))
            or not math.isfinite(rate)
            or rate <= 0
        ):
            raise ValueError(
                f"{name} must be a finite positive number."
            )

    @staticmethod
    def exponential_interarrival(arrival_rate, rng=None):
        DistributionGenerator._validate_rate(
            arrival_rate, "Arrival rate"
        )

        rng = rng or random.Random()
        return rng.expovariate(arrival_rate)

    @staticmethod
    def exponential_service(service_rate, rng=None):
        DistributionGenerator._validate_rate(
            service_rate, "Service rate"
        )

        rng = rng or random.Random()
        return rng.expovariate(service_rate)

    @staticmethod
    def deterministic_interarrival(arrival_rate):
        DistributionGenerator._validate_rate(
            arrival_rate, "Arrival rate"
        )

        return 1.0 / arrival_rate

    @staticmethod
    def deterministic_service(service_rate):
        DistributionGenerator._validate_rate(
            service_rate, "Service rate"
        )

        return 1.0 / service_rate

    @staticmethod
    def generate_customers(
        customer_count,
        arrival_rate,
        service_rate,
        arrival_distribution="exponential",
        service_distribution="exponential",
        seed=None,
    ):
        if (
            isinstance(customer_count, bool)
            or not isinstance(customer_count, int)
            or customer_count < 1
        ):
            raise ValueError(
                "Customer count must be a positive integer."
            )

        DistributionGenerator._validate_rate(
            arrival_rate, "Arrival rate"
        )
        DistributionGenerator._validate_rate(
            service_rate, "Service rate"
        )

        if arrival_distribution not in (
            "exponential",
            "deterministic",
        ):
            raise ValueError("Unsupported arrival distribution.")

        if service_distribution not in (
            "exponential",
            "deterministic",
        ):
            raise ValueError("Unsupported service distribution.")

        if seed is not None and (
            isinstance(seed, bool) or not isinstance(seed, int)
        ):
            raise ValueError("Seed must be an integer or None.")

        rng = random.Random(seed)
        customers = []
        arrival_time = 0.0

        for index in range(customer_count):
            if index > 0:
                if arrival_distribution == "exponential":
                    interval = rng.expovariate(arrival_rate)
                else:
                    interval = 1.0 / arrival_rate

                arrival_time += interval

            if service_distribution == "exponential":
                service_time = rng.expovariate(service_rate)
            else:
                service_time = 1.0 / service_rate

            customers.append({
                "customer_id": f"C{index + 1}",
                "arrival_time": round(arrival_time, 6),
                "service_time": round(service_time, 6),
            })

        return customers