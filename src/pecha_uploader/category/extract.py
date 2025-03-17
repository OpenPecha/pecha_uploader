import urllib
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url, headers, logger


def get_category(category_name: str, destination_url: Destination_url):
    """
    Check full category path for variable `category_name`.
        `category_name`: str, example: "Indian Treatises/Madyamika/The way of the bodhisattvas"
    """
    url = destination_url.value + "api/category/" + urllib.parse.quote(category_name)
    req = urllib.request.Request(url, method="GET", headers=headers)

    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        return res
    except HTTPError as e:
        error_message = f"HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        logger.error(error_message)
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"{e}"
        logger.error(error_message)
        raise Exception(error_message)
