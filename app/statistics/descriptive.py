import numpy as np


class DescriptiveStatistics:

    def __init__(self, customers):
        self.customers = customers

    def _values(self, attribute):
        values = []

        for customer in self.customers:
            value = getattr(customer, attribute, None)

            if value is not None:
                values.append(float(value))

        return values

    def _mean(self, values):
        if not values:
            return None

        return float(np.mean(values))

    def _minimum(self, values):
        if not values:
            return None

        return float(np.min(values))

    def _maximum(self, values):
        if not values:
            return None

        return float(np.max(values))

    def summary(self):

        outside_wait = self._values(
            "outside_wait_min"
        )

        main_wait = self._values(
            "main_wait_min"
        )

        total_time = self._values(
            "total_time_min"
        )

        service_times = [
            customer.service_time_min
            for customer in self.customers
            if customer.service_time_min is not None
        ]

        arrival_times = self._values(
            "arrival_min"
        )

        completed = [
            customer
            for customer in self.customers
            if (
                not customer.reneged
                and customer.service_end_min is not None
            )
        ]

        reneged = [
            customer
            for customer in self.customers
            if customer.reneged
        ]

        genders = {}

        for customer in self.customers:

            gender = customer.gender or "Unknown"

            genders[gender] = (
                genders.get(gender, 0) + 1
            )

        return {
            "total_customers": len(self.customers),

            "completed_customers": len(completed),

            "reneged_customers": len(reneged),

            "completion_rate": (
                len(completed) / len(self.customers) * 100
                if self.customers
                else 0
            ),

            "reneging_rate": (
                len(reneged) / len(self.customers) * 100
                if self.customers
                else 0
            ),

            "arrival": {
                "minimum": self._minimum(arrival_times),
                "maximum": self._maximum(arrival_times),
            },

            "outside_wait": {
                "average": self._mean(outside_wait),
                "minimum": self._minimum(outside_wait),
                "maximum": self._maximum(outside_wait),
            },

            "main_wait": {
                "average": self._mean(main_wait),
                "minimum": self._minimum(main_wait),
                "maximum": self._maximum(main_wait),
            },

            "service_time": {
                "average": self._mean(service_times),
                "minimum": self._minimum(service_times),
                "maximum": self._maximum(service_times),
            },

            "total_time": {
                "average": self._mean(total_time),
                "minimum": self._minimum(total_time),
                "maximum": self._maximum(total_time),
            },

            "gender_distribution": genders,
        }