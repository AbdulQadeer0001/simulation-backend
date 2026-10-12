import math
from flask import Blueprint, jsonify, request
from app.queueing.mm1 import MM1Queue
from app.queueing.mmc import MMCQueue



queueing_bp = Blueprint(
    "queueing",
    __name__
)


@queueing_bp.post("/queueing/mm1")
def calculate_mm1():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Provide a JSON request body."
        }), 400

    try:
        arrival_rate = data.get("arrival_rate")
        service_rate = data.get("service_rate")

        if arrival_rate is None or service_rate is None:
            return jsonify({
                "status": "error",
                "message": (
                    "arrival_rate and service_rate are required."
                )
            }), 400

        model = MM1Queue(
            arrival_rate=arrival_rate,
            service_rate=service_rate
        )

        result = model.calculate()

        return jsonify({
            "status": "success",
            "result": result
        }), 200

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400
        
@queueing_bp.post("/queueing/mmc")
def calculate_mmc():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Provide a JSON request body."
        }), 400

    try:
        arrival_rate = data.get("arrival_rate")
        service_rate = data.get("service_rate")
        server_count = data.get("server_count")

        if (
            arrival_rate is None
            or service_rate is None
            or server_count is None
        ):
            return jsonify({
                "status": "error",
                "message": (
                    "arrival_rate, service_rate, and "
                    "server_count are required."
                )
            }), 400

        # Reject fractional server counts instead of silently truncating.
        if isinstance(server_count, bool):
            raise ValueError("Server count must be a positive integer.")

        numeric_server_count = float(server_count)

        if (
            not math.isfinite(numeric_server_count)
            or not numeric_server_count.is_integer()
        ):
            raise ValueError("Server count must be a positive integer.")

        model = MMCQueue(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            server_count=int(numeric_server_count),
        )

        return jsonify({
            "status": "success",
            "result": model.calculate()
        }), 200

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400