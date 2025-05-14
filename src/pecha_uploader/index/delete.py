import urllib
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, headers


def remove_index(index_key: str, destination_url: str):
    """
    index_key > index title
    """
    index_key = index_key.replace(" ", "_")
    url = destination_url + f"api/index/{index_key}"
    values = {"apikey": PECHA_API_KEY}
    data = urllib.parse.urlencode(values)
    binary_key = data.encode("ascii")
    headers["apiKey"] = PECHA_API_KEY
    req = urllib.request.Request(url, binary_key, method="DELETE", headers=headers)
    try:
        urllib.request.urlopen(req)
        # res = urllib.request.urlopen(req)

    except HTTPError as e:
        error_message = (
            f"Index delete:HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        )
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"Index delete {e}"
        raise Exception(error_message)
