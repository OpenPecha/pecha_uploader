import json
import urllib.request
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url, headers, logger


def get_text(text_name: str, destination_url: Destination_url):
    """
    Get text value for article `text_name`.
        `text_name`: str, article name
    """
    text_url = destination_url.value + "api/texts"
    prepare_text_str = urllib.parse.quote(text_name)

    url = f"{text_url}/{prepare_text_str}?pad=0"
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        response = urllib.request.urlopen(req)  # noqa
        res = response.read().decode("utf-8")
        return json.loads(res)

    except HTTPError as e:
        error_message = f"HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        logger.error(error_message)
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"{e}"
        logger.error(error_message)
        raise Exception(error_message)
