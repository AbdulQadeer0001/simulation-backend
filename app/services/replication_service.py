
import math

from app.models.simulation_customer import SimulationCustomer
from app.services.simulation_service import SimulationService
from app.simulation.distributions import DistributionGenerator
from app.statistics.replication_statistics import ReplicationStatistics


class ReplicationService:
    """Run independent stochastic queueing simulation replications."""

    MAX_REPLICATIONS = 1000

    @staticmethod
    def run_replications(
        simulation_type,
        customer_count,
        arrival_rate,
        service_rate,
        replication_count=30,
        server_count=1,
        arrival_distribution="exponential",
        service_distribution="exponential",
        seed=None,
        confidence_level=0.95,
    ):
        # Validate simulation type.
        
        # Validate confidence level before running simulations.
        if (
            isinstance(confidence_level, bool)
            or not isinstance(confidence_level, (int, float))
            or not math.isfinite(confidence_level)
            or not 0 < confidence_level < 1
        ):
            raise ValueError(
                "confidence_level must be a number between 0 and 1."
            )
        if simulation_type not in ("single_server", "multi_server"):
            raise ValueError(
                "simulation_type must be 'single_server' "
                "or 'multi_server'."
            )

        # Validate customer count.
        if (
            isinstance(customer_count, bool)
            or not isinstance(customer_count, int)
            or customer_count < 1
        ):
            raise ValueError(
                "customer_count must be a positive integer."
            )

        # Validate replication count.
        if (
            isinstance(replication_count, bool)
            or not isinstance(replication_count, int)
            or not 2 <= replication_count <= ReplicationService.MAX_REPLICATIONS
        ):
            raise ValueError(
                "replication_count must be an integer between 2 and 1000."
            )

        # Validate rates.
        for name, value in (
            ("arrival_rate", arrival_rate),
            ("service_rate", service_rate),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError(
                    f"{name} must be a finite positive number."
                )

        # Validate server count.
        if simulation_type == "single_server":
            server_count = 1
        elif (
            isinstance(server_count, bool)
            or not isinstance(server_count, int)
            or server_count < 1
        ):
            raise ValueError(
                "server_count must be a positive integer."
            )

        # Validate seed.
        if seed is not None and (
            isinstance(seed, bool) or not isinstance(seed, int)
        ):
            raise ValueError("seed must be an integer or null.")

        results = []

        for replication_index in range(replication_count):
            # A different seed gives each replication a different
            # stochastic dataset. The same base seed reproduces
            # the entire sequence of replications.
            replication_seed = (
                None
                if seed is None
                else seed + replication_index
            )

            generated_customers = (
                DistributionGenerator.generate_customers(
                    customer_count=customer_count,
                    arrival_rate=arrival_rate,
                    service_rate=service_rate,
                    arrival_distribution=arrival_distribution,
                    service_distribution=service_distribution,
                    seed=replication_seed,
                )
            )

            customers = [
                SimulationCustomer(
                    customer_id=item["customer_id"],
                    arrival_min=item["arrival_time"],
                    service_time_min=item["service_time"],
                )
                for item in generated_customers
            ]

            if simulation_type == "single_server":
                result = SimulationService.run_single_server(
                    customers
                )
            else:
                result = SimulationService.run_multi_server(
                    customers,
                    server_count,
                )

            results.append(result)

        summary = ReplicationStatistics.summarize_results(
            results,
            confidence_level=confidence_level,
        )

        # Return summary statistics and each replication's metrics.
        return {
            "simulation_type": simulation_type,
            "server_count": server_count,
            "customer_count_per_replication": customer_count,
            "arrival_rate": arrival_rate,
            "service_rate": service_rate,
            "arrival_distribution": arrival_distribution,
            "service_distribution": service_distribution,
            "base_seed": seed,
            "summary": summary,
            "replications": [
                {
                    "replication": index + 1,
                    "customers_processed": result.customers_processed,
                    "average_waiting_time": result.average_waiting_time,
                    "average_system_time": result.average_system_time,
                    "average_number_in_queue": (
                        result.average_number_in_queue
                    ),
                    "average_number_in_system": (
                        result.average_number_in_system
                    ),
                    "utilization": result.utilization,
                    "throughput": result.throughput,
                }
                for index, result in enumerate(results)
            ],
        }