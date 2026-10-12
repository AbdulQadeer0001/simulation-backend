
from app.models.simulation_result import (
    CustomerSimulationResult,
    SimulationResult,
)

from app.statistics.time_based import TimeBasedStatistics


class MultiServerSimulation:

    def __init__(self, customers, server_count):

        if server_count < 1:
            raise ValueError(
                "Server count must be at least 1."
            )

        self.customers = customers
        self.server_count = server_count

    def run(self):

        if not self.customers:
            raise ValueError(
                "No customers available for simulation."
            )

        # Process customers in arrival order.
        customers = sorted(
            self.customers,
            key=lambda customer: (
                customer.arrival_min is None,
                customer.arrival_min
                if customer.arrival_min is not None
                else 0
            )
        )

        # Track the availability of each server.
        server_available_times = [
            0.0 for _ in range(self.server_count)
        ]

        server_idle_times = [
            0.0 for _ in range(self.server_count)
        ]

        customer_results = []

        for customer in customers:

            arrival_time = customer.arrival_min

            if arrival_time is None:
                continue

            service_time = customer.service_time_min

            if service_time is None:
                continue

            if service_time < 0:
                raise ValueError(
                    f"Negative service time for "
                    f"customer {customer.customer_id}."
                )

            # Select the server that becomes available first.
            server_index = min(
                range(self.server_count),
                key=lambda index: (
                    server_available_times[index],
                    index
                )
            )

            server_available_time = (
                server_available_times[server_index]
            )

            # Calculate server idle time and service start.
            if arrival_time > server_available_time:

                idle_time = (
                    arrival_time - server_available_time
                )

                service_start = arrival_time

                server_idle_times[server_index] += (
                    idle_time
                )

            else:
                idle_time = 0.0
                service_start = server_available_time

            waiting_time = (
                service_start - arrival_time
            )

            service_end = (
                service_start + service_time
            )

            system_time = (
                service_end - arrival_time
            )

            # Update the selected server's availability.
            server_available_times[server_index] = (
                service_end
            )

            result = CustomerSimulationResult(
                customer_id=customer.customer_id,
                arrival_time=round(arrival_time, 3),
                service_time=round(service_time, 3),
                service_start=round(service_start, 3),
                service_end=round(service_end, 3),
                waiting_time=round(waiting_time, 3),
                system_time=round(system_time, 3),
                server_id=server_index + 1,
                server_idle_time=round(idle_time, 3),
            )

            customer_results.append(result)

        return self._build_summary(
            customer_results,
            server_idle_times
        )

    def _build_summary(
        self,
        customer_results,
        server_idle_times
    ):

        if not customer_results:
            raise ValueError(
                "No valid customers were available "
                "for simulation."
            )

        # Calculate time-weighted statistics.
        time_stats = TimeBasedStatistics.calculate(
            customer_results,
            server_count=self.server_count
        )

        total_customers = len(customer_results)

        total_service_time = sum(
            result.service_time
            for result in customer_results
        )

        total_waiting_time = sum(
            result.waiting_time
            for result in customer_results
        )

        total_system_time = sum(
            result.system_time
            for result in customer_results
        )

        first_arrival = min(
            result.arrival_time
            for result in customer_results
        )

        last_departure = max(
            result.service_end
            for result in customer_results
        )

        simulation_time = (
            last_departure - first_arrival
        )

        if simulation_time <= 0:
            raise ValueError(
                "Simulation time must be greater than zero."
            )

        arrival_rate = (
            total_customers / simulation_time
        )

        service_rate = (
            total_customers / total_service_time
            if total_service_time > 0
            else None
        )

        average_waiting_time = (
            total_waiting_time / total_customers
        )

        average_system_time = (
            total_system_time / total_customers
        )

        throughput = (
            total_customers / simulation_time
        )

        total_idle_time = sum(server_idle_times)

        return SimulationResult(
            simulation_type="multi_server",
            server_count=self.server_count,
            customers_processed=total_customers,

            arrival_rate=round(arrival_rate, 6),

            service_rate=(
                round(service_rate, 6)
                if service_rate is not None
                else None
            ),

            utilization=time_stats["utilization"],

            average_waiting_time=round(
                average_waiting_time, 6
            ),

            average_system_time=round(
                average_system_time, 6
            ),

            average_number_in_queue=(
                time_stats["average_number_in_queue"]
            ),

            average_number_in_system=(
                time_stats["average_number_in_system"]
            ),

            throughput=round(throughput, 6),

            total_idle_time=round(
                total_idle_time, 6
            ),

            server_utilization=(
                time_stats["server_utilization"]
            ),

            customer_results=customer_results,
        )