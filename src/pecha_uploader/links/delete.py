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
        logger.info(f"Successfully removed link for: {text_title}")

    except HTTPError as e:
        # Handle HTTP errors
        logger.error(
            f"HTTP Error {e.code} occurred while removing link: {e.read().decode('utf-8')}"
        )
        raise HTTPError(f"HTTP Error occurred while removing link: {e.code}")

    except Exception as e:
        # Handle other exceptions
        logger.error(f"Unexpected error occurred: {e}", exc_info=True)
        raise Exception(f"An unexpected error occurred while removing link: {e}")
