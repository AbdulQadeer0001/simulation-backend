
from dataclasses import asdict, is_dataclass


class ResultFormatter:
    """Convert QueueLab simulation results into exportable rows."""

    @staticmethod
    def customer_rows(simulation_result):
        if not hasattr(simulation_result, "customer_results"):
            raise ValueError(
                "Expected a SimulationResult object."
            )

        customers = simulation_result.customer_results

        if not customers:
            raise ValueError(
                "Simulation result contains no customer results."
            )

        rows = []

        for customer in customers:
            if not is_dataclass(customer):
                raise ValueError(
                    "Customer results must be dataclass objects."
                )

            row = asdict(customer)
            row["simulation_type"] = (
                simulation_result.simulation_type
            )
            row["server_count"] = simulation_result.server_count

            rows.append(row)

        return rows

    @staticmethod
    def summary_rows(simulation_result):
        if not is_dataclass(simulation_result):
            raise ValueError(
                "Expected a SimulationResult dataclass."
            )

        result = asdict(simulation_result)

        # Customer-level details belong in a separate export.
        result.pop("customer_results", None)

        # Keep the per-server utilization values in a separate,
        # clearly named field.
        result["server_utilization"] = dict(
            simulation_result.server_utilization
        )

        return [result]

