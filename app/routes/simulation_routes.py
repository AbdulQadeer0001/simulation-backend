import os
import math
from flask import (
    Blueprint,
    current_app,
    jsonify,
    Response,
    request
)

from app.services.export_service import ExportService

from app.services.comparison_service import ComparisonService

from app.services.replication_service import ReplicationService

from app.statistics.input_data import summarize_customers

from app.data_processing.upload_loader import SimulationUploadLoader

from app.simulation.distributions import DistributionGenerator


from app.models.simulation_customer import SimulationCustomer

from app.data_processing.nadra_loader import (
    NADRADataLoader
)

from app.simulation.single_server import (
    SingleServerSimulation
)

from app.services.simulation_service import SimulationService


simulation_bp = Blueprint(
    "simulation",
    __name__
)


@simulation_bp.get(
    "/simulation/single-server/nadra"
)
def run_nadra_single_server():

    file_path = os.path.join(
    current_app.config["OBSERVED_DATA_FOLDER"],
    "nadra_day1_first100.xlsx"
    )

    try:

        loader = NADRADataLoader(
            file_path
        )

        customers = loader.load()

        simulation = SingleServerSimulation(
            customers
        )

        result = simulation.run()

        customer_results = []

        for customer in result.customer_results:

            customer_results.append({

                "customer_id":
                    customer.customer_id,

                "arrival_time":
                    customer.arrival_time,

                "service_time":
                    customer.service_time,

                "service_start":
                    customer.service_start,

                "service_end":
                    customer.service_end,

                "waiting_time":
                    customer.waiting_time,

                "system_time":
                    customer.system_time,

                "server_idle_time":
                    customer.server_idle_time,
            })

        return jsonify({

            "status": "success",

            "simulation": {
                "type":
                    result.simulation_type,

                "servers":
                    result.server_count,

                "customers_processed":
                    result.customers_processed,

                "arrival_rate":
                    result.arrival_rate,

                "service_rate":
                    result.service_rate,

                "utilization":
                    result.utilization,

                "average_waiting_time":
                    result.average_waiting_time,

                "average_system_time":
                    result.average_system_time,

                "average_number_in_queue":
                    result.average_number_in_queue,

                "average_number_in_system":
                    result.average_number_in_system,

                "throughput":
                    result.throughput,

                "total_idle_time":
                    result.total_idle_time,
            },

            "customers":
                customer_results
        })

    except Exception as error:

        return jsonify({

            "status": "error",

            "message": str(error)

        }), 500
        
@simulation_bp.get(
    "/simulation/multi-server/nadra/<int:server_count>"
)
def run_nadra_multi_server(server_count):

    file_path = os.path.join(
        current_app.config[
            "OBSERVED_DATA_FOLDER"
        ],
        "nadra_day1_first100.xlsx",
    )

    try:

        loader = NADRADataLoader(
            file_path
        )

        customers = loader.load()

        result = (
            SimulationService
            .run_multi_server(
                customers,
                server_count
            )
        )

        customer_results = []

        for customer in result.customer_results:

            customer_results.append({

                "customer_id":
                    customer.customer_id,

                "arrival_time":
                    customer.arrival_time,

                "service_time":
                    customer.service_time,

                "service_start":
                    customer.service_start,

                "service_end":
                    customer.service_end,

                "waiting_time":
                    customer.waiting_time,

                "system_time":
                    customer.system_time,

                "server_id":
                    customer.server_id,

                "server_idle_time":
                    customer.server_idle_time,
            })

        return jsonify({

            "status": "success",

            "simulation": {

                "type":
                    result.simulation_type,

                "server_count":
                    result.server_count,

                "customers_processed":
                    result.customers_processed,

                "arrival_rate":
                    result.arrival_rate,

                "service_rate":
                    result.service_rate,

                "utilization":
                    result.utilization,

                "average_waiting_time":
                    result.average_waiting_time,

                "average_system_time":
                    result.average_system_time,

                "average_number_in_queue":
                    result.average_number_in_queue,

                "average_number_in_system":
                    result.average_number_in_system,

                "throughput":
                    result.throughput,

                "total_idle_time":
                    result.total_idle_time,

                "server_utilization":
                    result.server_utilization,
            },

            "customers":
                customer_results,
        })

    except Exception as error:

        return jsonify({

            "status": "error",

            "message": str(error),

        }), 500
        

@simulation_bp.post("/simulation/run")
def run_custom_simulation():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Provide a valid JSON request body.",
        }), 400

    try:
        simulation_type = data.get("simulation_type")
        customers_data = data.get("customers")

        if simulation_type not in ("single_server", "multi_server"):
            return jsonify({
                "status": "error",
                "message": (
                    "simulation_type must be 'single_server' "
                    "or 'multi_server'."
                ),
            }), 400

        if not isinstance(customers_data, list) or not customers_data:
            return jsonify({
                "status": "error",
                "message": "customers must be a non-empty list.",
            }), 400

        server_count = 1

        if simulation_type == "multi_server":
            raw_count = data.get("server_count")

            if isinstance(raw_count, bool) or raw_count is None:
                raise ValueError(
                    "server_count must be a positive integer."
                )

            numeric_count = float(raw_count)

            if (
                not math.isfinite(numeric_count)
                or not numeric_count.is_integer()
                or numeric_count < 1
            ):
                raise ValueError(
                    "server_count must be a positive integer."
                )

            server_count = int(numeric_count)

        customers = []
        customer_ids = set()

        for index, item in enumerate(customers_data, start=1):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Customer at index {index - 1} must be an object."
                )

            customer_id = item.get(
                "customer_id",
                f"Customer-{index:03d}",
            )

            if not isinstance(customer_id, str) or not customer_id.strip():
                raise ValueError(
                    f"Customer at index {index - 1} "
                    "must have a valid customer_id."
                )

            customer_id = customer_id.strip()

            if customer_id in customer_ids:
                raise ValueError(
                    f"Duplicate customer_id: {customer_id}."
                )

            customer_ids.add(customer_id)

            arrival_time = item.get("arrival_time")
            service_time = item.get("service_time")

            if arrival_time is None or service_time is None:
                raise ValueError(
                    f"Customer {customer_id} must include "
                    "arrival_time and service_time."
                )

            if isinstance(arrival_time, bool) or isinstance(service_time, bool):
                raise ValueError(
                    f"Customer {customer_id} has invalid time values."
                )

            arrival_time = float(arrival_time)
            service_time = float(service_time)

            if (
                not math.isfinite(arrival_time)
                or not math.isfinite(service_time)
            ):
                raise ValueError(
                    f"Customer {customer_id} has non-finite time values."
                )

            if arrival_time < 0:
                raise ValueError(
                    f"Arrival time for {customer_id} cannot be negative."
                )

            if service_time <= 0:
                raise ValueError(
                    f"Service time for {customer_id} must be greater than zero."
                )

            customers.append(
                SimulationCustomer(
                    customer_id=customer_id,
                    arrival_min=arrival_time,
                    service_time_min=service_time,
                )
            )

        if simulation_type == "single_server":
            result = SimulationService.run_single_server(customers)
        else:
            result = SimulationService.run_multi_server(
                customers,
                server_count,
            )

        return jsonify({
            "status": "success",
            "simulation": {
                "type": result.simulation_type,
                "server_count": result.server_count,
                "customers_processed": result.customers_processed,
                "arrival_rate": result.arrival_rate,
                "service_rate": result.service_rate,
                "utilization": result.utilization,
                "average_waiting_time": result.average_waiting_time,
                "average_system_time": result.average_system_time,
                "average_number_in_queue": (
                    result.average_number_in_queue
                ),
                "average_number_in_system": (
                    result.average_number_in_system
                ),
                "throughput": result.throughput,
                "total_idle_time": result.total_idle_time,
                "server_utilization": result.server_utilization,
            },
            "customers": [
                {
                    "customer_id": customer.customer_id,
                    "arrival_time": customer.arrival_time,
                    "service_time": customer.service_time,
                    "service_start": customer.service_start,
                    "service_end": customer.service_end,
                    "waiting_time": customer.waiting_time,
                    "system_time": customer.system_time,
                    "server_id": customer.server_id,
                    "server_idle_time": customer.server_idle_time,
                }
                for customer in result.customer_results
            ],
        }), 200

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "status": "error",
            "message": str(error),
        }), 400
        

@simulation_bp.post("/simulation/generate-and-run")
def generate_and_run_simulation():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Provide a valid JSON request body.",
        }), 400

    try:
        simulation_type = data.get("simulation_type", "single_server")
        customer_count = data.get("customer_count")
        arrival_rate = data.get("arrival_rate")
        service_rate = data.get("service_rate")
        arrival_distribution = data.get(
            "arrival_distribution", "exponential"
        )
        service_distribution = data.get(
            "service_distribution", "exponential"
        )
        seed = data.get("seed")
        server_count = data.get("server_count", 1)

        if simulation_type not in ("single_server", "multi_server"):
            raise ValueError(
                "simulation_type must be 'single_server' "
                "or 'multi_server'."
            )

        if (
            isinstance(customer_count, bool)
            or not isinstance(customer_count, int)
            or customer_count < 1
        ):
            raise ValueError(
                "customer_count must be a positive integer."
            )

        for name, value in (
            ("arrival_rate", arrival_rate),
            ("service_rate", service_rate),
        ):
            if isinstance(value, bool) or value is None:
                raise ValueError(f"{name} must be a positive number.")

            if not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be a positive number.")

            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a finite positive number.")

        if simulation_type == "single_server":
            server_count = 1
        else:
            if (
                isinstance(server_count, bool)
                or not isinstance(server_count, int)
                or server_count < 1
            ):
                raise ValueError(
                    "server_count must be a positive integer."
                )

        if seed is not None and (
            isinstance(seed, bool) or not isinstance(seed, int)
        ):
            raise ValueError("seed must be an integer or null.")

        generated_customers = DistributionGenerator.generate_customers(
            customer_count=customer_count,
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            arrival_distribution=arrival_distribution,
            service_distribution=service_distribution,
            seed=seed,
        )

        customers = [
            SimulationCustomer(
                customer_id=item["customer_id"],
                arrival_min=item["arrival_time"],
                service_time_min=item["service_time"],
            )
            for item in generated_customers
        ]

        if simulation_type == "single_server":
            result = SimulationService.run_single_server(customers)
        else:
            result = SimulationService.run_multi_server(
                customers,
                server_count,
            )

        return jsonify({
            "status": "success",
            "configuration": {
                "simulation_type": simulation_type,
                "customer_count": customer_count,
                "arrival_rate": arrival_rate,
                "service_rate": service_rate,
                "arrival_distribution": arrival_distribution,
                "service_distribution": service_distribution,
                "server_count": server_count,
                "seed": seed,
                "time_unit": "minutes",
            },
            "simulation": {
                "type": result.simulation_type,
                "server_count": result.server_count,
                "customers_processed": result.customers_processed,
                "arrival_rate": result.arrival_rate,
                "service_rate": result.service_rate,
                "utilization": result.utilization,
                "average_waiting_time": result.average_waiting_time,
                "average_system_time": result.average_system_time,
                "average_number_in_queue": (
                    result.average_number_in_queue
                ),
                "average_number_in_system": (
                    result.average_number_in_system
                ),
                "throughput": result.throughput,
                "total_idle_time": result.total_idle_time,
                "server_utilization": result.server_utilization,
            },
            "customers": [
                {
                    "customer_id": customer.customer_id,
                    "arrival_time": customer.arrival_time,
                    "service_time": customer.service_time,
                    "service_start": customer.service_start,
                    "service_end": customer.service_end,
                    "waiting_time": customer.waiting_time,
                    "system_time": customer.system_time,
                    "server_id": customer.server_id,
                    "server_idle_time": customer.server_idle_time,
                }
                for customer in result.customer_results
            ],
        }), 200

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "status": "error",
            "message": str(error),
        }), 400
        

@simulation_bp.post("/simulation/upload-and-run")
def upload_and_run_simulation():
    uploaded_file = request.files.get("file")

    if uploaded_file is None:
        return jsonify({
            "status": "error",
            "message": "Upload a file using the 'file' field.",
        }), 400

    simulation_type = request.form.get(
        "simulation_type", "single_server"
    ).strip().lower()

    if simulation_type not in ("single_server", "multi_server"):
        return jsonify({
            "status": "error",
            "message": (
                "simulation_type must be 'single_server' "
                "or 'multi_server'."
            ),
        }), 400

    try:
        server_count = 1

        if simulation_type == "multi_server":
            raw_count = request.form.get("server_count")

            if raw_count is None or not raw_count.strip():
                raise ValueError(
                    "server_count is required for multi-server simulation."
                )

            try:
                numeric_count = float(raw_count)
            except (ValueError, OverflowError) as error:
                raise ValueError(
                    "server_count must be a positive integer."
                ) from error

            if (
                not math.isfinite(numeric_count)
                or not numeric_count.is_integer()
                or numeric_count < 1
            ):
                raise ValueError(
                    "server_count must be a positive integer."
                )

            server_count = int(numeric_count)

        customers = SimulationUploadLoader.load(uploaded_file)

        if simulation_type == "single_server":
            result = SimulationService.run_single_server(customers)
        else:
            result = SimulationService.run_multi_server(
                customers,
                server_count,
            )

        return jsonify({
            "status": "success",
            "source": "uploaded_file",
            "filename": uploaded_file.filename,
            "time_unit": "minutes",
            "simulation": {
                "type": result.simulation_type,
                "server_count": result.server_count,
                "customers_processed": result.customers_processed,
                "arrival_rate": result.arrival_rate,
                "service_rate": result.service_rate,
                "utilization": result.utilization,
                "average_waiting_time": result.average_waiting_time,
                "average_system_time": result.average_system_time,
                "average_number_in_queue": (
                    result.average_number_in_queue
                ),
                "average_number_in_system": (
                    result.average_number_in_system
                ),
                "throughput": result.throughput,
                "total_idle_time": result.total_idle_time,
                "server_utilization": result.server_utilization,
            },
            "customers": [
                {
                    "customer_id": customer.customer_id,
                    "arrival_time": customer.arrival_time,
                    "service_time": customer.service_time,
                    "service_start": customer.service_start,
                    "service_end": customer.service_end,
                    "waiting_time": customer.waiting_time,
                    "system_time": customer.system_time,
                    "server_id": customer.server_id,
                    "server_idle_time": customer.server_idle_time,
                }
                for customer in result.customer_results
            ],
        }), 200

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "status": "error",
            "message": str(error),
        }), 400
        
@simulation_bp.post("/statistics/describe-upload")
def describe_uploaded_data():
    uploaded_file = request.files.get("file")

    try:
        customers = SimulationUploadLoader.load(uploaded_file)

        statistics = summarize_customers(customers)

        return jsonify({
            "status": "success",
            "source": "uploaded_file",
            "filename": uploaded_file.filename,
            "statistics": statistics,
        }), 200

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "status": "error",
            "message": str(error),
        }), 400
        

@simulation_bp.post("/simulation/replicate")
def run_replications():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    try:
        result = ReplicationService.run_replications(
            simulation_type=data.get("simulation_type", "single_server"),
            customer_count=data.get("customer_count", 100),
            arrival_rate=data.get("arrival_rate", 0.5),
            service_rate=data.get("service_rate", 1.0),
            replication_count=data.get("replication_count", 30),
            server_count=data.get("server_count", 1),
            arrival_distribution=data.get(
                "arrival_distribution", "exponential"
            ),
            service_distribution=data.get(
                "service_distribution", "exponential"
            ),
            seed=data.get("seed"),
            confidence_level=data.get("confidence_level", 0.95),
        )

        return jsonify(result), 200

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400
    
@simulation_bp.post("/simulation/compare")
def compare_simulation_scenarios():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    try:
        result = ComparisonService.compare_scenarios(
            data.get("scenarios")
        )

        return jsonify(result), 200

    except (ValueError, TypeError) as error:
        return jsonify({
            "error": str(error)
        }), 400
        

@simulation_bp.post("/simulation/export/csv")
def export_simulation_csv():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    try:
        csv_content = ExportService.to_csv(data.get("rows"))

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                    'attachment; filename="queuelab_results.csv"'
            },
        )

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@simulation_bp.post("/simulation/export/excel")
def export_simulation_excel():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    try:
        excel_content = ExportService.to_excel(data.get("rows"))

        return Response(
            excel_content,
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                    'attachment; filename="queuelab_results.xlsx"'
            },
        )

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400
    
    

def _run_simulation_for_export(data):
    """Validate inputs, run a simulation, and return its result."""

    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object.")

    simulation_type = data.get("simulation_type", "single_server")

    if simulation_type not in ("single_server", "multi_server"):
        raise ValueError(
            "simulation_type must be 'single_server' or 'multi_server'."
        )

    customer_count = data.get("customer_count", 100)
    arrival_rate = data.get("arrival_rate", 0.5)
    service_rate = data.get("service_rate", 1.0)
    arrival_distribution = data.get(
        "arrival_distribution", "exponential"
    )
    service_distribution = data.get(
        "service_distribution", "exponential"
    )
    seed = data.get("seed")
    server_count = data.get("server_count", 1)

    # Validate integer inputs. Booleans are not accepted as integers.
    if (
        isinstance(customer_count, bool)
        or not isinstance(customer_count, int)
        or customer_count <= 0
    ):
        raise ValueError("customer_count must be a positive integer.")

    if (
        isinstance(server_count, bool)
        or not isinstance(server_count, int)
        or server_count <= 0
    ):
        raise ValueError("server_count must be a positive integer.")

    # Validate rates as finite, positive numbers.
    for name, value in (
        ("arrival_rate", arrival_rate),
        ("service_rate", service_rate),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a positive finite number.")

        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a positive finite number.")

    if seed is not None and (
        isinstance(seed, bool) or not isinstance(seed, int)
    ):
        raise ValueError("seed must be an integer or null.")

    supported_distributions = ("exponential", "deterministic")

    if arrival_distribution not in supported_distributions:
        raise ValueError(
            "arrival_distribution must be 'exponential' "
            "or 'deterministic'."
        )

    if service_distribution not in supported_distributions:
        raise ValueError(
            "service_distribution must be 'exponential' "
            "or 'deterministic'."
        )

    generated_customers = DistributionGenerator.generate_customers(
        customer_count=customer_count,
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        arrival_distribution=arrival_distribution,
        service_distribution=service_distribution,
        seed=seed,
    )

    customers = [
        SimulationCustomer(
            customer_id=item["customer_id"],
            arrival_min=item["arrival_time"],
            service_time_min=item["service_time"],
        )
        for item in generated_customers
    ]
    
    if simulation_type == "single_server":
        return SimulationService.run_single_server(customers)

    return SimulationService.run_multi_server(
        customers,
        server_count,
    )


@simulation_bp.post("/simulation/run-and-export/csv")
def run_and_export_csv():
    data = request.get_json(silent=True)

    try:
        result = _run_simulation_for_export(data)

        export_type = data.get("export_type", "customers")

        csv_content = ExportService.simulation_to_csv(
            result,
            export_type=export_type,
        )

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={
                "Content-Disposition": (
                    'attachment; filename="queuelab_simulation.csv"'
                )
            },
        )

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "status": "error",
            "message": str(error),
        }), 400


@simulation_bp.post("/simulation/run-and-export/excel")
def run_and_export_excel():
    data = request.get_json(silent=True)

    try:
        result = _run_simulation_for_export(data)

        export_type = data.get("export_type", "customers")

        excel_content = ExportService.simulation_to_excel(
            result,
            export_type=export_type,
        )

        return Response(
            excel_content,
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (
                    'attachment; filename="queuelab_simulation.xlsx"'
                )
            },
        )

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "status": "error",
            "message": str(error),
        }), 400

