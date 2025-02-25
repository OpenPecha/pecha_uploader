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


def get_term(term: str):
    """
    Get term values for variable `term_str`.
        `term`: str, term name
    """
    url = baseURL + "api/terms/" + urllib.parse.quote(term)
    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req)  # noqa
        res = response.read().decode("utf-8")
        log_info(text_info_logger, f"term: {res}")
        return {"status": True}
    except HTTPError as e:
        # error_message = e.read().decode("utf-8")
        log_error(text_error_logger, f"HTTPError while fetching term '{term} {e}'")
        return {"status": False}

    except Exception as e:
        log_error(
            text_error_logger,
            f"Unexpected error while fetching term '{term}': {str(e)}",
        )
        return {"status": False}
