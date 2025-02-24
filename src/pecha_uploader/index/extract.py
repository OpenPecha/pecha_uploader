import urllib
from urllib.error import HTTPError

from pecha_uploader.config import baseURL, headers, logger


def get_index(index: str):
    """
    Get Index information for article name `index`.
        `index`: str, article en name
    """
    index_url = baseURL + "api/v2/raw/index"
    prepare_index_str = index.replace(" ", "_")
    url = f"{index_url}/{prepare_index_str}?with_content_counts=1"
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        response = urllib.request.urlopen(req)  # noqa
    except HTTPError as e:
        # Handle HTTP errors
        logger.error(
            f"HTTP Error {e.code} occurred extracting index: {e.read().decode('utf-8')}"
        )
        raise HTTPError(f"HTTP Error occurred while removing link: {e.code}")

    except Exception as e:
        # Handle other exceptions
        logger.error(f"Unexpected error occurred: {e}", exc_info=True)
        raise Exception(f"An unexpected error occurred extracting index: {e}")
