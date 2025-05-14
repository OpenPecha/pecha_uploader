import urllib
from urllib.error import HTTPError

from pecha_uploader.config import headers


def get_index(index: str, destination_url: str):
    """
    Get Index information for article name `index`.
        `index`: str, article en name
    """
    index_url = destination_url + "api/v2/raw/index"
    prepare_index_str = index.replace(" ", "_")
    url = f"{index_url}/{prepare_index_str}?with_content_counts=1"
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        response = urllib.request.urlopen(req)  # noqa
        res = response.read().decode("utf-8")
        return res
    except HTTPError as e:
        error_message = (
            f"Index extract: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        )
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"Index extract: {e}"
        raise Exception(error_message)
