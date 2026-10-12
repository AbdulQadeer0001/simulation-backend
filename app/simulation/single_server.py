
from app.models.simulation_result import (
    CustomerSimulationResult,
    SimulationResult,
)

from app.statistics.time_based import TimeBasedStatistics


class SingleServerSimulation:

    def __init__(self, customers):
        self.customers = customers

    def run(self):

        if not self.customers:
            raise ValueError(
                "No customers available for simulation."
            )

        # Sort customers by arrival time.
        customers = sorted(
            self.customers,
            key=lambda customer: (
                customer.arrival_min is None,
                customer.arrival_min
                if customer.arrival_min is not None
                else 0
            )
        )

        customer_results = []
        server_available_time = 0.0
        total_idle_time = 0.0

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

            # Determine when service can begin.
            if arrival_time > server_available_time:

                idle_time = (
                    arrival_time - server_available_time
                )

                total_idle_time += idle_time
                service_start = arrival_time

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

            server_available_time = service_end

            result = CustomerSimulationResult(
                customer_id=customer.customer_id,
                arrival_time=round(arrival_time, 3),
                service_time=round(service_time, 3),
                service_start=round(service_start, 3),
                service_end=round(service_end, 3),
                waiting_time=round(waiting_time, 3),
                system_time=round(system_time, 3),
                server_id=1,
                server_idle_time=round(idle_time, 3),
            )

            customer_results.append(result)

        return self._build_summary(
            customer_results,
            total_idle_time
        )

    def _build_summary(
        self,
        customer_results,
        total_idle_time
    ):

        if not customer_results:
            raise ValueError(
                "No valid customers were available "
                "for simulation."
            )

        # Calculate statistics directly from event times.
        time_stats = TimeBasedStatistics.calculate(
            customer_results,
            server_count=1
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

        return SimulationResult(
            simulation_type="single_server",
            server_count=1,
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