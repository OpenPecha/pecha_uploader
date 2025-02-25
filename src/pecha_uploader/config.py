import logging
import os
from enum import Enum
from pathlib import Path

PECHA_API_KEY = os.environ.get("PECHA_API_KEY")


def _mkdir_if_not(path: Path):
    """Create a directory if it does not exist"""
    path.mkdir(exist_ok=True, parents=True)
    return path


# Paths
BASE_PATH = _mkdir_if_not(Path.home() / ".pecha_uploader")
TEXT_PATH = _mkdir_if_not(BASE_PATH / "texts")
LINK_PATH = _mkdir_if_not(BASE_PATH / "links")
LINK_JSON_PATH = _mkdir_if_not(LINK_PATH / "jsons")

TEXT_ERROR_LOG = TEXT_PATH / "errors.txt"
TEXT_ERROR_ID_LOG = TEXT_PATH / "errors_text_id.txt"
TEXT_SUCCESS_LOG = TEXT_PATH / "success.txt"
TEXT_INFO_LOG = TEXT_PATH / "info.txt"  # <--- New Info Log

LINK_ERROR_LOG = LINK_PATH / "errors.txt"
LINK_ERROR_ID_LOG = LINK_PATH / "errors_link_id.txt"
LINK_SUCCESS_LOG = LINK_PATH / "success.txt"
LINK_INFO_LOG = LINK_PATH / "info.txt"  # <--- New Info Log


# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")


def setup_logger(name, log_file, level=logging.INFO):
    """Set up a logger for different log files"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File Handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Console Handler (for warnings and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    # Avoid duplicate handlers
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Loggers for different purposes
text_error_logger = setup_logger("text_error_logger", TEXT_ERROR_LOG, logging.ERROR)
text_success_logger = setup_logger(
    "text_success_logger", TEXT_SUCCESS_LOG, logging.INFO
)
text_info_logger = setup_logger("text_info_logger", TEXT_INFO_LOG, logging.INFO)
link_error_logger = setup_logger("link_error_logger", LINK_ERROR_LOG, logging.ERROR)
link_success_logger = setup_logger(
    "link_success_logger", LINK_SUCCESS_LOG, logging.INFO
)
link_info_logger = setup_logger("link_info_logger", LINK_INFO_LOG, logging.INFO)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"  # noqa
}
BASEPATH = os.path.dirname(os.path.abspath(__file__))  # Path to `Pecha.org/tools`


class Destination_url(Enum):
    PRODUCTION = "https://pecha.org/"
    STAGING = "https://staging.pecha.org/"
    LOCAL = "http://127.0.0.1:8000/"


def log_error(logger, message: str):
    """Log an error message"""
    logger.error(f" {message}")


def log_success(logger, text_name: str):
    """Log a success message"""
    logger.info(f"{text_name}")


def log_info(logger, message: str):
    """Log an informational message"""
    logger.info(f"{message}")


def set_api_key(api_key: str):
    if not api_key:
        raise ValueError("PECHA API KEY is not given properly.")
    os.environ["PECHA_API_KEY"] = api_key
