import re
import urllib
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers, logger


def remove_links(text_title: str, destination_url: Destination_url):
    """
    text_title > Reference link of text. e.g Prayer 1:1 or Prayer 1:1-2
    """
    # remove section range number from text title. e.g Prayer 1:1, Prayer 1:1-2
    pattern = r"\s\d+:\d+(-\d+)?"
    clean_title = re.sub(pattern, "", text_title)

    ref = clean_title.replace(" ", "_")
    url = destination_url.value + f"api/links/{ref}"
    values = {"apikey": PECHA_API_KEY}
    data = urllib.parse.urlencode(values)
    binary_key = data.encode("ascii")
    req = urllib.request.Request(url, binary_key, method="DELETE", headers=headers)
    try:
        urllib.request.urlopen(req)
        # # response = urllib.request.urlopen(req)
        # logger.info(f"Successfully removed link for: {text_title}")

    except HTTPError as e:
        error_message = (
            f"LINK: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        )
        logger.error(error_message)
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"LINK: {e}"
        logger.error(error_message)
        raise Exception(error_message)
