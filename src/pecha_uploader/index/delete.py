import urllib
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers, logger


def remove_index(index_key: str, destination_url: Destination_url):
    """
    index_key > index title
    """
    index_key = index_key.replace(" ", "_")
    url = destination_url.value + f"api/index/{index_key}"
    values = {"apikey": PECHA_API_KEY}
    data = urllib.parse.urlencode(values)
    binary_key = data.encode("ascii")
    headers["apiKey"] = PECHA_API_KEY
    req = urllib.request.Request(url, binary_key, method="DELETE", headers=headers)
    try:
        urllib.request.urlopen(req)
        # res = urllib.request.urlopen(req)
        logger.info("Deleted existing index")

    except HTTPError as e:
        error_message = f"HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        logger.error(error_message)
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"{e}"
        logger.error(error_message)
        raise Exception(error_message)
