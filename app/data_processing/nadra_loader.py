import pandas as pd

from app.models.customer import Customer


COLUMN_MAPPING = {
    "Day": "day",
    "# in Day": "sequence_number",
    "Customer ID": "customer_id",
    "Gender": "gender",

    "Arrival (min)": "arrival_min",
    "Arrival (date/time)": "arrival_datetime",

    "Admitted (min)": "admitted_min",
    "Admitted (date/time)": "admitted_datetime",

    "Queue1 Token Start (min)": "token_start_min",
    "Queue1 Token Start (date/time)": "token_start_datetime",

    "Queue1 Token End (min)": "token_end_min",
    "Queue1 Token End (date/time)": "token_end_datetime",

    "Queue2 Main Wait Start (min)": "main_wait_start_min",
    "Queue2 Main Wait Start (date/time)": "main_wait_start_datetime",

    "Queue3 Service Start (min)": "service_start_min",
    "Queue3 Service Start (date/time)": "service_start_datetime",

    "Queue3 Service End (min)": "service_end_min",
    "Queue3 Service End (date/time)": "service_end_datetime",

    "Reneged": "reneged",

    "Outside Wait (min)": "outside_wait_min",
    "Main Wait (min)": "main_wait_min",
    "Total Time (min)": "total_time_min",
}


REQUIRED_COLUMNS = [
    "Customer ID",
    "Arrival (min)",
    "Reneged",
]


NUMERIC_COLUMNS = [
    "day",
    "sequence_number",
    "arrival_min",
    "admitted_min",
    "token_start_min",
    "token_end_min",
    "main_wait_start_min",
    "service_start_min",
    "service_end_min",
    "outside_wait_min",
    "main_wait_min",
    "total_time_min",
]


class NADRADataLoader:

    def __init__(self, file_path):
        self.file_path = file_path

    def load_excel(self):
        """Read the Excel file into a Pandas DataFrame."""
        return pd.read_excel(self.file_path)

    def validate_columns(self, df):
        """Check whether required columns exist."""

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in df.columns
        ]

        return missing_columns

    def normalize_columns(self, df):
        """Rename Excel columns to QueueLab's internal names."""

        df = df.rename(columns=COLUMN_MAPPING)

        return df

    def clean_data(self, df):
        """Convert values into consistent data types."""

        # Numeric columns
        for column in NUMERIC_COLUMNS:
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        # Gender
        if "gender" in df.columns:
            df["gender"] = (
                df["gender"]
                .astype("string")
                .str.strip()
            )

        # Customer ID
        if "customer_id" in df.columns:
            df["customer_id"] = (
                df["customer_id"]
                .astype("string")
                .str.strip()
            )

        # Reneged
        if "reneged" in df.columns:
            df["reneged"] = (
                df["reneged"]
                .fillna(False)
                .astype(bool)
            )

        return df

    def convert_to_customers(self, df):
        """Convert DataFrame rows into Customer objects."""

        customers = []

        for _, row in df.iterrows():

            customer = Customer(
                day=self._value(row, "day"),
                sequence_number=self._value(
                    row,
                    "sequence_number"
                ),
                customer_id=str(
                    self._value(row, "customer_id")
                ),
                gender=self._value(row, "gender"),

                arrival_min=self._value(
                    row,
                    "arrival_min"
                ),
                arrival_datetime=self._datetime_value(
                    row,
                    "arrival_datetime"
                ),

                admitted_min=self._value(
                    row,
                    "admitted_min"
                ),
                admitted_datetime=self._datetime_value(
                    row,
                    "admitted_datetime"
                ),

                token_start_min=self._value(
                    row,
                    "token_start_min"
                ),
                token_start_datetime=self._datetime_value(
                    row,
                    "token_start_datetime"
                ),

                token_end_min=self._value(
                    row,
                    "token_end_min"
                ),
                token_end_datetime=self._datetime_value(
                    row,
                    "token_end_datetime"
                ),

                main_wait_start_min=self._value(
                    row,
                    "main_wait_start_min"
                ),
                main_wait_start_datetime=self._datetime_value(
                    row,
                    "main_wait_start_datetime"
                ),

                service_start_min=self._value(
                    row,
                    "service_start_min"
                ),
                service_start_datetime=self._datetime_value(
                    row,
                    "service_start_datetime"
                ),

                service_end_min=self._value(
                    row,
                    "service_end_min"
                ),
                service_end_datetime=self._datetime_value(
                    row,
                    "service_end_datetime"
                ),

                reneged=bool(
                    self._value(row, "reneged")
                ),

                outside_wait_min=self._value(
                    row,
                    "outside_wait_min"
                ),
                main_wait_min=self._value(
                    row,
                    "main_wait_min"
                ),
                total_time_min=self._value(
                    row,
                    "total_time_min"
                ),
            )

            customers.append(customer)

        return customers

    def load(self):
        """Complete loading pipeline."""

        df = self.load_excel()

        missing_columns = self.validate_columns(df)

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        df = self.normalize_columns(df)

        df = self.clean_data(df)

        customers = self.convert_to_customers(df)

        return customers

    @staticmethod
    def _value(row, column):

        value = row.get(column)

        if pd.isna(value):
            return None

        return value

    @staticmethod
    def _datetime_value(row, column):

        value = row.get(column)

        if pd.isna(value):
            return None

        return str(value)