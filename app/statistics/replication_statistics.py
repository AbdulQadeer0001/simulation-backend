
from math import sqrt
from statistics import mean, stdev

from scipy.stats import t


class ReplicationStatistics:

    METRICS = (
        "average_waiting_time",
        "average_system_time",
        "average_number_in_queue",
        "average_number_in_system",
        "utilization",
        "throughput",
    )

    @staticmethod
    def summarize(values, confidence_level=0.95):
        """
        Summarize a numeric metric across independent replications.
        """

        
        if (
            isinstance(confidence_level, bool)
            or not isinstance(confidence_level, (int, float))
            or not 0 < confidence_level < 1
        ):
            raise ValueError(
                "Confidence level must be a number between 0 and 1."
            )

        if not values:
            raise ValueError(
                "At least one replication is required."
            )

        if any(
            value is None
            or isinstance(value, bool)
            or not isinstance(value, (int, float))
            for value in values
        ):
            raise ValueError(
                "Replication values must be numeric."
            )

        if any(
            not __import__("math").isfinite(value)
            for value in values
        ):
            raise ValueError(
                "Replication values must be finite."
            )

        count = len(values)
        average = mean(values)

        if count == 1:
            return {
                "replication_count": 1,
                "mean": round(average, 6),
                "standard_deviation": None,
                "confidence_level": confidence_level,
                "confidence_interval": None,
            }

        standard_deviation = stdev(values)
        standard_error = standard_deviation / sqrt(count)

        critical_value = t.ppf(
            (1 + confidence_level) / 2,
            df=count - 1,
        )

        margin_of_error = critical_value * standard_error

        return {
            "replication_count": count,
            "mean": round(average, 6),
            "standard_deviation": round(
                standard_deviation, 6
            ),
            "confidence_level": confidence_level,
            "confidence_interval": {
                "lower": round(
                    average - margin_of_error, 6
                ),
                "upper": round(
                    average + margin_of_error, 6
                ),
                "margin_of_error": round(
                    margin_of_error, 6
                ),
            },
        }

    @classmethod
    def summarize_results(
        cls,
        simulation_results,
        confidence_level=0.95,
    ):
        """
        Summarize supported metrics across SimulationResult objects.
        """

        if not simulation_results:
            raise ValueError(
                "At least one simulation result is required."
            )

        summaries = {}

        for metric in cls.METRICS:
            values = [
                getattr(result, metric)
                for result in simulation_results
            ]

            # Some metrics may be unavailable for every run.
            if all(value is None for value in values):
                summaries[metric] = None
                continue

            if any(value is None for value in values):
                raise ValueError(
                    f"Metric '{metric}' is missing "
                    "from some replications."
                )

            summaries[metric] = cls.summarize(
                values,
                confidence_level=confidence_level,
            )

        return {
            "replication_count": len(simulation_results),
            "confidence_level": confidence_level,
            "metrics": summaries,
        }