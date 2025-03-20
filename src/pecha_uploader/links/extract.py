import urllib
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url, headers


def get_link(link_name: str, destination_url: Destination_url, with_text=1):
    """
    Get links for article/section/row `link_name`
        `link_name`: str, article/section/row name
            article  => link_name = "The way of the bodhisattvas"
            section  => link_name = "The way of the bodhisattvas.1"
            sections => link_name = "The way of the bodhisattvas.1-2"
            row      => link_name = "The way of the bodhisattvas.1:1"
            rows     => link_name = "The way of the bodhisattvas.1:1-3"
    """
    link_name = link_name.replace(" ", "_")
    link_url = ""
    for c in link_name:
        if ord(c) > 128:
            link_url += urllib.parse.quote(c)
        else:
            link_url += c
    url = destination_url.value + f"api/links/{link_url}?with_text={with_text}"
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        response = urllib.request.urlopen(req)  # noqa
        res = response.read().decode("utf-8")
        return res

    except HTTPError as e:
        error_message = (
            f"Link extract: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        )
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"Link extract: {e}"
        raise Exception(error_message)
