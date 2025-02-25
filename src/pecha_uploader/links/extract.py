import urllib
from urllib.error import HTTPError

from pecha_uploader.config import baseURL, headers, link_error_logger, log_error


def get_link(link_name: str, with_text=1):
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
    url = baseURL + f"api/links/{link_url}?with_text={with_text}"
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        response = urllib.request.urlopen(req)  # noqa
        return {"status": True, "data": response}
    except HTTPError as e:
        # Handle HTTP errors (e.g., 404, 500, etc.)
        log_error(link_error_logger, f"HTTP Error occurred. Status code: {e.code}")
        return {"status": False}

    except Exception as e:
        # Handle other unexpected errors (e.g., network issues, invalid URLs, etc.)
        log_error(link_error_logger, f"An unexpected error occurred: {e}")
        return {"status": False}
