
from dataclasses import dataclass


@dataclass
class SimulationCustomer:
    customer_id: str
    arrival_min: float
    service_time_min: float