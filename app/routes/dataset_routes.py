import os

from flask import Blueprint, current_app, jsonify

from app.data_processing.nadra_loader import NADRADataLoader
from app.statistics.descriptive import DescriptiveStatistics


dataset_bp = Blueprint(
    "dataset",
    __name__
)


@dataset_bp.get("/dataset/nadra")
def get_nadra_dataset():

    file_path = os.path.join(
        current_app.config["OBSERVED_DATA_FOLDER"],
        "nadra_day1_first100.xlsx",
    )

    try:

        loader = NADRADataLoader(file_path)

        customers = loader.load()

        statistics = DescriptiveStatistics(
            customers
        )

        summary = statistics.summary()

        preview = []

        for customer in customers[:10]:

            preview.append({
                "customer_id": customer.customer_id,
                "gender": customer.gender,
                "arrival_min": customer.arrival_min,
                "admitted_min": customer.admitted_min,
                "token_start_min": customer.token_start_min,
                "token_end_min": customer.token_end_min,
                "service_start_min": customer.service_start_min,
                "service_end_min": customer.service_end_min,
                "reneged": customer.reneged,
                "outside_wait_min": customer.outside_wait_min,
                "main_wait_min": customer.main_wait_min,
                "total_time_min": customer.total_time_min,
                "service_time_min": customer.service_time_min,
            })

        return jsonify({
            "status": "success",
            "dataset": "NADRA Day 1 First 100",
            "customer_count": len(customers),
            "summary": summary,
            "preview": preview,
        })

    except Exception as error:

        return jsonify({
            "status": "error",
            "message": str(error),
        }), 500
