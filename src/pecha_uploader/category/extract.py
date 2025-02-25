import urllib
from urllib.error import HTTPError

from pecha_uploader.config import text_info_logger  # <--- Import the Info Logger
from pecha_uploader.config import (
    baseURL,
    headers,
    log_error,
    log_info,
    text_error_logger,
)


def get_category(category_name: str):
    """
    Check full category path for variable `category_name`.
        `category_name`: str, example: "Indian Treatises/Madyamika/The way of the bodhisattvas"
    """
    url = baseURL + "api/category/" + urllib.parse.quote(category_name)
    req = urllib.request.Request(url, method="GET", headers=headers)

    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        if "error" not in res:
            log_info(text_info_logger, f"{res}")
            return {"status": True}
        elif "already exists" in res["error"]:
            log_info(text_info_logger, f"Category already exists : {category_name}")
            return {"status": True}
        log_error(text_error_logger, f"Category check failed: {res}")
        return {"status": False}
    except HTTPError as e:
        error_message = e.read().decode("utf-8")
        log_error(
            text_error_logger,
            f"HTTPError while fetching category {{category_name}}: {error_message}",
        )
        return {"status": False}

    except Exception as e:
        log_error(
            text_error_logger,
            f"Unexpected error while fetching category {category_name}: {str(e)}",
        )
        return {"status": False}
