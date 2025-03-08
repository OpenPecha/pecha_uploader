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


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Create a logger instance
logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"  # noqa
}
BASEPATH = os.path.dirname(os.path.abspath(__file__))  # Path to `Pecha.org/tools`


class Destination_url(Enum):
    PRODUCTION = "https://pecha.org/"
    STAGING = "https://staging.pecha.org/"
    LOCAL = "http://127.0.0.1:8000/"


def log_link_success(text_name: str):
    with open(LINK_SUCCESS_LOG, "w") as f:
        f.write(text_name + "\n")


def set_api_key(api_key: str):
    if not api_key:
        raise ValueError("PECHA API KEY is not given properly.")
    os.environ["PECHA_API_KEY"] = api_key
