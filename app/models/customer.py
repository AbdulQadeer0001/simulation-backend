from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    day: Optional[int]
    sequence_number: Optional[int]
    customer_id: str
    gender: Optional[str]

    arrival_min: Optional[float]
    arrival_datetime: Optional[str]

    admitted_min: Optional[float]
    admitted_datetime: Optional[str]

    token_start_min: Optional[float]
    token_start_datetime: Optional[str]

    token_end_min: Optional[float]
    token_end_datetime: Optional[str]

    main_wait_start_min: Optional[float]
    main_wait_start_datetime: Optional[str]

    service_start_min: Optional[float]
    service_start_datetime: Optional[str]

    service_end_min: Optional[float]
    service_end_datetime: Optional[str]

    reneged: bool

    outside_wait_min: Optional[float]
    main_wait_min: Optional[float]
    total_time_min: Optional[float]

    @property
    def service_time_min(self):
        if (
            self.service_start_min is not None
            and self.service_end_min is not None
        ):
            return round(
                self.service_end_min - self.service_start_min,
                3
            )

        return None