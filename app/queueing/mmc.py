import math


class MMCQueue:
    def __init__(self, arrival_rate, service_rate, server_count):
        self.arrival_rate = float(arrival_rate)
        self.service_rate = float(service_rate)
        self.server_count = int(server_count)

        if not math.isfinite(self.arrival_rate):
            raise ValueError("Arrival rate must be finite.")

        if not math.isfinite(self.service_rate):
            raise ValueError("Service rate must be finite.")

        if self.arrival_rate <= 0:
            raise ValueError("Arrival rate must be greater than zero.")

        if self.service_rate <= 0:
            raise ValueError("Service rate must be greater than zero.")

        if self.server_count < 1:
            raise ValueError("Server count must be at least 1.")

        if self.arrival_rate >= self.server_count * self.service_rate:
            raise ValueError(
                "M/M/c is unstable: arrival rate must be less than "
                "the total service capacity."
            )

    def calculate(self):
        lam = self.arrival_rate
        mu = self.service_rate
        c = self.server_count

        a = lam / mu
        rho = lam / (c * mu)

        # Calculate the first c terms of the steady-state probability.
        sum_terms = sum(
            (a ** n) / math.factorial(n)
            for n in range(c)
        )

        # Add the probability-series tail for states n >= c.
        tail = (
            (a ** c)
            / (math.factorial(c) * (1 - rho))
        )

        probability_empty = 1 / (sum_terms + tail)

        # Erlang C: probability that an arriving customer must wait.
        probability_wait = tail * probability_empty

        average_number_in_queue = (
            probability_wait * rho / (1 - rho)
        )

        average_number_in_system = (
            average_number_in_queue + a
        )

        average_waiting_time = (
            average_number_in_queue / lam
        )

        average_system_time = (
            average_waiting_time + 1 / mu
        )

        return {
            "model": "M/M/c",
            "assumptions": {
                "arrival_distribution": "Poisson",
                "service_distribution": "Exponential",
                "server_count": c,
                "queue_capacity": "Unlimited",
                "queue_discipline": "FCFS",
                "steady_state": True,
            },
            "input": {
                "arrival_rate": lam,
                "service_rate_per_server": mu,
                "server_count": c,
                "utilization": round(rho, 6),
            },
            "metrics": {
                "probability_empty": round(probability_empty, 6),
                "probability_wait": round(probability_wait, 6),
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
                    average_system_time, 6
                ),
                "throughput": lam,
            },
        }