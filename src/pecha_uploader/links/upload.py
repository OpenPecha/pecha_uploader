import json
import urllib
from typing import List
from urllib.error import HTTPError

from pecha_uploader.config import link_info_logger  # <--- Import the Info Logger
from pecha_uploader.config import (
    PECHA_API_KEY,
    Destination_url,
    headers,
    link_error_logger,
    log_error,
    log_info,
)


def post_link(ref_list: List[str], type_str: str, destination_url: Destination_url):
    """
    Post references for articles.
        `ref_list`: list of str, articles to reference
            ref_list = [
                "Article_1.1:2",    # First article/section/row
                "Article_2.1:2"     # Second
            ]
        `type_str`: str, reference type
            The Sefaria team have provided several types:
                - commentary
                - quotation
                - reference
                - summary
                - explication
                - related
    """
    url = destination_url.value + "api/links/"
    link = {"refs": ref_list, "type": type_str}
    input_json_link = json.dumps(link)

    values = {"json": input_json_link, "apikey": PECHA_API_KEY}
    data = urllib.parse.urlencode(values)
    binary_data = data.encode("ascii")
    req = urllib.request.Request(url, binary_data, headers=headers)
    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        if "error" not in res:
            log_info(link_info_logger, f"Link successfully created: {ref_list['refs']}")
            return {"status": True}
        elif "Link already exists" in res:
            log_info(link_info_logger, f"Link already exists: {ref_list['refs']}")
            return {"status": False}
        log_info(link_info_logger, f"Link creation failed: {res}")
        return {"status": False}
    except HTTPError as e:
        error_message = e.read().decode("utf-8")
        log_error(
            link_error_logger,
            f"HTTPError while posting link: {error_message}",
            exc_info=True,
        )
        return {"status": False}

    except Exception as e:
        log_error(link_error_logger, f"Unexpected error while posting link: {str(e)}")
        return {"status": False}
