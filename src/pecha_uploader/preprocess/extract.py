import json
import urllib
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url, headers, logger


def get_term(term: str, destination_url: Destination_url):
    """
    Get term values for variable `term_str`.
        `term`: str, term name
    """
    url = destination_url.value + "api/terms/" + urllib.parse.quote(term)
    req = urllib.request.Request(url, headers=headers)
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
