
import math
from pathlib import Path

import pandas as pd

from app.models.simulation_customer import SimulationCustomer


class SimulationUploadLoader:
    REQUIRED_COLUMNS = {
        "arrival_time",
        "service_time",
    }

    @staticmethod
    def load(file_storage):
        if file_storage is None or not file_storage.filename:
            raise ValueError("No file was uploaded.")

        extension = Path(file_storage.filename).suffix.lower()

        if extension not in {".csv", ".xlsx", ".xls"}:
            raise ValueError(
                "Unsupported file type. Upload CSV, XLSX, or XLS."
            )

        try:
            if extension == ".csv":
                dataframe = pd.read_csv(file_storage)
            else:
                dataframe = pd.read_excel(file_storage)
        except Exception as error:
            raise ValueError(
                "Could not read the uploaded file. Check its format."
            ) from error

        if dataframe.empty:
            raise ValueError("The uploaded file contains no customers.")

        if len(dataframe) > 100000:
            raise ValueError(
                "The file exceeds the limit of 100,000 customers."
            )

        # Normalize headers, but don't silently rename data columns.
        dataframe.columns = [
            str(column).strip().lower()
            for column in dataframe.columns
        ]

        if dataframe.columns.duplicated().any():
            raise ValueError(
                "The file contains duplicate column names."
            )

        missing = (
            SimulationUploadLoader.REQUIRED_COLUMNS
            - set(dataframe.columns)
        )

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing))
            )

        customers = []
        seen_ids = set()

        for index, row in dataframe.iterrows():
            row_number = index + 2

            arrival_value = row["arrival_time"]
            service_value = row["service_time"]

            if (
                pd.isna(arrival_value)
                or pd.isna(service_value)
                or isinstance(arrival_value, bool)
                or isinstance(service_value, bool)
            ):
                raise ValueError(
                    f"Row {row_number}: arrival_time and "
                    "service_time must be numeric."
                )

            try:
                arrival_time = float(arrival_value)
                service_time = float(service_value)
            except (ValueError, TypeError, OverflowError) as error:
                raise ValueError(
                    f"Row {row_number}: arrival_time and "
                    "service_time must be numeric."
                ) from error

            if not math.isfinite(arrival_time) or not math.isfinite(
                service_time
            ):
                raise ValueError(
                    f"Row {row_number}: time values must be finite."
                )

            if arrival_time < 0:
                raise ValueError(
                    f"Row {row_number}: arrival_time cannot be negative."
                )

            if service_time <= 0:
                raise ValueError(
                    f"Row {row_number}: service_time must be positive."
                )

            if "customer_id" in dataframe.columns:
                raw_id = row["customer_id"]

                if pd.isna(raw_id) or not str(raw_id).strip():
                    customer_id = f"Customer-{len(customers) + 1:03d}"
                else:
                    customer_id = str(raw_id).strip()
            else:
                customer_id = f"Customer-{len(customers) + 1:03d}"

            if customer_id in seen_ids:
                raise ValueError(
                    f"Row {row_number}: duplicate customer_id "
                    f"'{customer_id}'."
                )

            seen_ids.add(customer_id)

            customers.append(
                SimulationCustomer(
                    customer_id=customer_id,
                    arrival_min=arrival_time,
                    service_time_min=service_time,
                )
            )

        return customers