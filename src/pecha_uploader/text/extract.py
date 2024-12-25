import urllib
from urllib.error import HTTPError

from pecha_uploader.config import baseURL, headers


def get_text(text_name: str):
    """
    Get text value for article `text_name`.
        `text_name`: str, article name
    """
    text_url = baseURL + "api/texts"
    prepare_text_str = urllib.parse.quote(text_name)

    url = f"{text_url}/{prepare_text_str}?pad=0"
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        response = urllib.request.urlopen(req)
        print(response.read().decode("utf-8"))
    except HTTPError as e:
        print("Error code: ", e.code)
        print(e.read().decode("utf-8"))
