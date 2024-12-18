import json
import urllib
from urllib.error import HTTPError

from pecha_uploader.config import baseURL, headers


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
        response = urllib.request.urlopen(req)
        print(json.loads(response.read().decode("utf-8")))
    except HTTPError as e:
        print("Error code: ", e.code)
        print(e.read().decode("utf-8"))
