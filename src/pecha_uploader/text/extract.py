import urllib
from urllib.error import HTTPError

from pecha_uploader.config import baseURL, headers, log_error, text_error_logger


def get_text(text_name: str):
    """
    Get text value for article `text_name`.
        `text_name`: str, article name
    """
    text_url = baseURL + "api/texts"
    prepare_text_str = urllib.parse.quote(text_name)

    url = f"{text_url}/{prepare_text_str}?pad=0"
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        response = urllib.request.urlopen(req)  # noqa
    except HTTPError as e:
        error_message = e.read().decode("utf-8")
        log_error(
            text_error_logger,
            f"HTTPError while fetching text '{text_name}': {error_message}",
        )
        return {"status": False}

    except Exception as e:
        log_error(
            text_error_logger,
            f"Unexpected error while fetching text '{text_name}': {str(e)}",
        )
        return {"status": False}
