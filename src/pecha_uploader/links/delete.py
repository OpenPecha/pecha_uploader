import re
import urllib
from urllib.error import HTTPError

from pecha_uploader.config import get_api_key, Destination_url, headers


def remove_links(text_title: str, destination_url: Destination_url):
    """
    text_title > Reference link of text. e.g Prayer 1:1 or Prayer 1:1-2
    """
    # remove section range number from text title. e.g Prayer 1:1, Prayer 1:1-2
    pattern = r"\s\d+:\d+(-\d+)?"
    clean_title = re.sub(pattern, "", text_title)

    ref = clean_title.replace(" ", "_")
    url = destination_url.value + f"api/links/{ref}"
    values = {"apikey": get_api_key()}
    data = urllib.parse.urlencode(values)
    binary_key = data.encode("ascii")
    req = urllib.request.Request(url, binary_key, method="DELETE", headers=headers)
    try:
        urllib.request.urlopen(req)

    except (HTTPError) as e:
        print("Error code: ", e.code)
        print("error", e.read())
