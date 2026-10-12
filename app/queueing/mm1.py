
import math


class MM1Queue:

    def __init__(self, arrival_rate, service_rate):
        self.arrival_rate = float(arrival_rate)
        self.service_rate = float(service_rate)

        if not math.isfinite(self.arrival_rate):
            raise ValueError(
                "Arrival rate must be a finite number."
            )

        if not math.isfinite(self.service_rate):
            raise ValueError(
                "Service rate must be a finite number."
            )

        if self.arrival_rate <= 0:
            raise ValueError(
                "Arrival rate must be greater than zero."
            )

        if self.service_rate <= 0:
            raise ValueError(
                "Service rate must be greater than zero."
            )

        if self.arrival_rate >= self.service_rate:
            raise ValueError(
                "M/M/1 is unstable: arrival rate must be "
                "less than service rate."
            )

    def calculate(self):

        lam = self.arrival_rate
        mu = self.service_rate

        # Server utilization.
        rho = lam / mu

        # Probability that the system is empty.
        probability_empty = 1 - rho

        # Average number of customers in the system.
        average_number_in_system = (
            lam / (mu - lam)
        )

        # Average number of customers waiting in the queue.
        average_number_in_queue = (
            lam ** 2 / (mu * (mu - lam))
        )

        # Average time spent in the system.
        average_time_in_system = (
            1 / (mu - lam)
        )

        # Average waiting time before service.
        average_waiting_time = (
            lam / (mu * (mu - lam))
        )

        return {
            "model": "M/M/1",
            "assumptions": {
                "arrival_distribution": "Poisson",
                "service_distribution": "Exponential",
                "server_count": 1,
                "queue_capacity": "Unlimited",
                "queue_discipline": "FCFS",
                "steady_state": True,
            },
            "input": {
                "arrival_rate": lam,
                "service_rate": mu,
                "utilization": round(rho, 6),
            },
            "metrics": {
                "probability_empty": round(
                    probability_empty, 6
                ),
                "average_number_in_queue": round(
                    average_number_in_queue, 6
                ),
                "average_number_in_system": round(
                    average_number_in_system, 6
                ),
                "average_waiting_time": round(
                    average_waiting_time, 6
                ),
                "average_system_time": round(
                    average_time_in_system, 6
                ),
                "throughput": lam,
            },
        }