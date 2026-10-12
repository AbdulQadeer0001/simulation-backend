
from app.services.replication_service import ReplicationService


class ComparisonService:
    """Compare multiple queueing simulation configurations."""

    @staticmethod
    def compare_scenarios(scenarios):
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError(
                "scenarios must be a non-empty list."
            )

        if len(scenarios) > 20:
            raise ValueError(
                "A maximum of 20 scenarios is allowed."
            )

        results = []

        
        for index, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict):
                raise ValueError(
                    f"Scenario {index + 1} must be an object."
                )

            scenario_name = scenario.get(
                "name", f"Scenario {index + 1}"
            )

            if (
                not isinstance(scenario_name, str)
                or not scenario_name.strip()
            ):
                raise ValueError(
                    f"Scenario {index + 1} name must be "
                    "a non-empty string."
                )

            result = ReplicationService.run_replications(
                simulation_type=scenario.get(
                    "simulation_type", "single_server"
                ),
                customer_count=scenario.get(
                    "customer_count", 100
                ),
                arrival_rate=scenario.get(
                    "arrival_rate", 0.5
                ),
                service_rate=scenario.get(
                    "service_rate", 1.0
                ),
                replication_count=scenario.get(
                    "replication_count", 30
                ),
                server_count=scenario.get(
                    "server_count", 1
                ),
                arrival_distribution=scenario.get(
                    "arrival_distribution", "exponential"
                ),
                service_distribution=scenario.get(
                    "service_distribution", "exponential"
                ),
                seed=scenario.get("seed", 42),
                confidence_level=scenario.get(
                    "confidence_level", 0.95
                ),
            )

            summary = result["summary"]["metrics"]

            results.append({
                "scenario_id": index + 1,
                "scenario_name": scenario_name,
                "simulation_type": result["simulation_type"],
                "server_count": result["server_count"],
                "customer_count_per_replication": (
                    result["customer_count_per_replication"]
                ),
                "arrival_rate": result["arrival_rate"],
                "service_rate": result["service_rate"],
                "arrival_distribution": (
                    result["arrival_distribution"]
                ),
                "service_distribution": (
                    result["service_distribution"]
                ),
                "replication_count": (
                    result["summary"]["replication_count"]
                ),
                "metrics": summary,
            })

        return {
            "scenario_count": len(results),
            "scenarios": results,
        }

