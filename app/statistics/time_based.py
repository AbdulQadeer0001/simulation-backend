
class TimeBasedStatistics:
    """
    Calculates time-weighted queue statistics from simulated
    customer arrival, service-start, and departure events.

    The observation period runs from the first arrival to the
    last departure.
    """

    @staticmethod
    def calculate(customer_results, server_count):
        if server_count < 1:
            raise ValueError(
                "Server count must be at least 1."
            )

        if not customer_results:
            raise ValueError(
                "Customer results cannot be empty."
            )

        first_arrival = min(
            customer.arrival_time
            for customer in customer_results
        )

        last_departure = max(
            customer.service_end
            for customer in customer_results
        )

        observation_time = (
            last_departure - first_arrival
        )

        if observation_time <= 0:
            raise ValueError(
                "Observation time must be greater than zero."
            )

        # Each event changes the population of a queue or system.
        queue_events = []
        system_events = []

        busy_time_by_server = {
            server_id: 0.0
            for server_id in range(1, server_count + 1)
        }

        for customer in customer_results:
            arrival = customer.arrival_time
            service_start = customer.service_start
            service_end = customer.service_end

            if not (
                arrival <= service_start <= service_end
            ):
                raise ValueError(
                    f"Invalid event times for customer "
                    f"{customer.customer_id}."
                )

            # Queue: +1 when arriving, -1 when service begins.
            queue_events.append((arrival, 1))
            queue_events.append((service_start, -1))

            # System: +1 on arrival, -1 on departure.
            system_events.append((arrival, 1))
            system_events.append((service_end, -1))

            busy_time_by_server[customer.server_id] += (
                service_end - service_start
            )

        
        def time_weighted_average(events):
            events.sort(key=lambda event: event[0])

            population = 0
            previous_time = first_arrival
            area = 0.0
            index = 0

            while index < len(events):
                event_time = events[index][0]

                # Accumulate population over the interval
                # before applying events at this timestamp.
                area += population * (
                    event_time - previous_time
                )

                # Apply all changes at the same timestamp
                # together, avoiding temporary negative counts.
                net_change = 0

                while (
                    index < len(events)
                    and events[index][0] == event_time
                ):
                    net_change += events[index][1]
                    index += 1

                population += net_change

                if population < 0:
                    raise ValueError(
                        "Invalid event sequence: population "
                        "became negative."
                    )

                previous_time = event_time

            area += population * (
                last_departure - previous_time
            )

            if population != 0:
                raise ValueError(
                    "Invalid event sequence: population "
                    "did not return to zero."
                )

            return area / observation_time

        average_queue_length = time_weighted_average(
            queue_events
        )

        average_system_population = time_weighted_average(
            system_events
        )

        server_utilization = {
            str(server_id): round(
                busy_time / observation_time,
                6
            )
            for server_id, busy_time
            in busy_time_by_server.items()
        }

        total_busy_time = sum(
            busy_time_by_server.values()
        )

        overall_utilization = (
            total_busy_time
            / (server_count * observation_time)
        )

        return {
            "observation_start": round(first_arrival, 3),
            "observation_end": round(last_departure, 3),
            "observation_time": round(
                observation_time, 6
            ),
            "average_number_in_queue": round(
                average_queue_length, 6
            ),
            "average_number_in_system": round(
                average_system_population, 6
            ),
            "utilization": round(
                overall_utilization, 6
            ),
            "server_utilization": server_utilization,
        }