import urllib
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers, logger


def remove_category(category_list: str, destination_url: Destination_url):
    """
    category_path > list of category path. e.g ["Liturgy", "Prayer"]
    """
    category_path = "/".join(category_list)
    url = destination_url.value + f"api/category/{urllib.parse.quote(category_path)}"
    values = {"apikey": PECHA_API_KEY}
    data = urllib.parse.urlencode(values)
    binary_key = data.encode("ascii")
    req = urllib.request.Request(url, binary_key, method="DELETE", headers=headers)
    try:
        urllib.request.urlopen(req)
        res = urllib.request.urlopen(req)
        response = res.read().decode("utf-8")
        logger.info(f"{response}")

    except HTTPError as e:
        error_message = f"HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        logger.error(error_message)
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"{e}"
        logger.error(error_message)
        raise Exception(error_message)
