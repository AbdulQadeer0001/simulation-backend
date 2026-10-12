from dataclasses import dataclass
from typing import Optional


@dataclass
class CustomerSimulationResult:
    customer_id: str

    arrival_time: float
    service_time: float

    service_start: float
    service_end: float

    waiting_time: float
    system_time: float

    server_id: int
    server_idle_time: float


@dataclass
class SimulationResult:
    simulation_type: str
    server_count: int

    customers_processed: int

    arrival_rate: Optional[float]
    service_rate: Optional[float]

    utilization: Optional[float]

    average_waiting_time: Optional[float]
    average_system_time: Optional[float]

    average_number_in_queue: Optional[float]
    average_number_in_system: Optional[float]

    throughput: Optional[float]

    total_idle_time: float

    server_utilization: dict

    customer_results: list