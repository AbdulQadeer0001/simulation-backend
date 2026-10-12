from flask import Blueprint, jsonify


health_bp = Blueprint(
    "health",
    __name__
)


@health_bp.get("/health")
def health_check():
    return jsonify({
        "status": "ok",
        "application": "QueueLab",
        "version": "0.1.0",
        "message": "QueueLab backend is running"
    })