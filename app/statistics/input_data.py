from statistics import mean, median, pstdev


def _percentile(values, percentile):
    """Calculate a percentile using linear interpolation."""
    if not values:
        return None

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * percentile
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(ordered) - 1)

    fraction = position - lower_index

    return (
        ordered[lower_index] * (1 - fraction)
        + ordered[upper_index] * fraction
    )


def _describe(values):
    """Calculate descriptive statistics for a numeric series."""
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "standard_deviation": None,
            "minimum": None,
            "maximum": None,
            "percentile_25": None,
            "percentile_50": None,
            "percentile_75": None,
        }

    return {
        "count": len(values),
        "mean": round(mean(values), 6),
        "median": round(median(values), 6),
        "standard_deviation": round(pstdev(values), 6),
        "minimum": round(min(values), 6),
        "maximum": round(max(values), 6),
        "percentile_25": round(_percentile(values, 0.25), 6),
        "percentile_50": round(_percentile(values, 0.50), 6),
        "percentile_75": round(_percentile(values, 0.75), 6),
    }


def summarize_customers(customers):
    """
    Summarize arrival and service data.

    Customers must have:
        arrival_min
        service_time_min
    """

    if not customers:
        raise ValueError("At least one customer is required.")

    arrival_times = sorted(
        float(customer.arrival_min)
        for customer in customers
    )

    service_times = [
        float(customer.service_time_min)
        for customer in customers
    ]

    interarrival_times = [
        arrival_times[index] - arrival_times[index - 1]
        for index in range(1, len(arrival_times))
    ]

    arrival_duration = (
        arrival_times[-1] - arrival_times[0]
    )

    arrival_rate = None

    if arrival_duration > 0:
        arrival_rate = (
            len(interarrival_times) / arrival_duration
        )

    average_service_time = mean(service_times)

    service_rate = (
        1 / average_service_time
        if average_service_time > 0
        else None
    )

    return {
        "customer_count": len(customers),
        "time_unit": "minutes",
        "arrival_times": _describe(arrival_times),
        "interarrival_times": _describe(interarrival_times),
        "service_times": _describe(service_times),
        "estimated_arrival_rate": (
            round(arrival_rate, 6)
            if arrival_rate is not None
            else None
        ),
        "estimated_service_rate": (
            round(service_rate, 6)
            if service_rate is not None
            else None
        ),
        "arrival_observation_duration": round(
            arrival_duration, 6
        ),
    }