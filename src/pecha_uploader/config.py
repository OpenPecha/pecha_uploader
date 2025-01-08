import os
from enum import Enum
from pathlib import Path


def _mkdir_if_not(path: Path):
    """Create a directory if it does not exist"""
    if not path.exists():
        path.mkdir(exist_ok=True, parents=True)
    return path


BASE_PATH = _mkdir_if_not(Path.home() / ".pecha_uploader")
TEXT_PATH = _mkdir_if_not(BASE_PATH / "texts")
LINK_PATH = _mkdir_if_not(BASE_PATH / "links")
LINK_JSON_PATH = _mkdir_if_not(LINK_PATH / "jsons")

TEXT_ERROR_LOG = TEXT_PATH / "errors.txt"
TEXT_ERROR_ID_LOG = TEXT_PATH / "errors_text_id.txt"
TEXT_SUCCESS_LOG = TEXT_PATH / "success.txt"

LINK_ERROR_LOG = LINK_PATH / "errors.txt"
LINK_ERROR_ID_LOG = LINK_PATH / "errors_link_id.txt"
LINK_SUCCESS_LOG = LINK_PATH / "success.txt"

PECHA_API_KEY = os.getenv("PECHA_API_KEY")
if not PECHA_API_KEY:
    raise ValueError("Please set PECHA_API_KEY environment variable")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"  # noqa
}
BASEPATH = os.path.dirname(os.path.abspath(__file__))  # path to `Pecha.org/tools`


class Destination_url(Enum):
    PRODUCTION = "https://pecha.org/"
    STAGING = "https://staging.pecha.org/"
    LOCAL = "http://127.0.0.1:8000/"


def log_error(file_name: Path, text_name: str, message: str):
    """Log error to file"""
    if not file_name.exists():
        make_empty_file(file_name)

    with open(file_name, "a", encoding="utf-8") as log_file:
        log_file.write(f"{text_name} : {message}\n")


def log_error_id(file_name: Path, text_name: str):
    """Log error with id to file"""
    if not file_name.exists():
        make_empty_file(file_name)
    with open(file_name, "a", encoding="utf-8") as log_file:
        log_file.write(f"{text_name}\n")


def log_success(file_name: Path, text_name: str):
    """Log success to file"""
    if not file_name.exists():
        make_empty_file(file_name)
    with open(file_name, "a", encoding="utf-8") as log_file:
        log_file.write(f"{text_name}\n")


def make_empty_file(file_name: Path):
    file_name.write_text("", encoding="utf-8")
