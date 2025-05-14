import urllib
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, str, headers, logger


def remove_text(title: str, destination_url: str):
    """
    title > text title
    """
    url = destination_url + f"api/texts/{title}"
    values = {"apikey": PECHA_API_KEY}
    data = urllib.parse.urlencode(values)
    binary_key = data.encode("ascii")
    req = urllib.request.Request(url, binary_key, method="DELETE", headers=headers)
    try:
        urllib.request.urlopen(req)
        # response = urllib.request.urlopen(req)
        logger.info(f"Successfully removed text for: {title}")

    except HTTPError as e:
        error_message = (
            f"Text delete: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        )
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"Text delete: {e}"
        raise Exception(error_message)
