import logging
import os
from enum import Enum

PECHA_API_KEY = os.environ.get("PECHA_API_KEY")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_logger(name):
    return logging.getLogger(name)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"  # noqa
}


class Destination_url(Enum):
    PRODUCTION = "https://pecha.org/"
    STAGING = "https://staging.pecha.org/"
    LOCAL = "http://127.0.0.1:8000/"


def set_api_key(api_key: str):
    """
    DONT DELETE: Being used by openpecha-backend to set api key
    """
    if not api_key:
        raise ValueError("PECHA API KEY is not given properly.")
    os.environ["PECHA_API_KEY"] = api_key
