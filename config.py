import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "queuelab-development-secret"
    )

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "data",
        "uploads"
    )

    OBSERVED_DATA_FOLDER = os.path.join(
        BASE_DIR,
        "data",
        "observed"
    )

    ALLOWED_EXTENSIONS = {
        "xlsx",
        "xls",
        "csv"
    }