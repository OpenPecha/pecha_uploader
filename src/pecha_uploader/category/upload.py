import json
from typing import List
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pecha_uploader.config import text_info_logger  # <--- Import the Info Logger
from pecha_uploader.config import (
    PECHA_API_KEY,
    Destination_url,
    headers,
    log_error,
    log_info,
    text_error_logger,
)


def post_category(
    en_category_list: List[str],
    bo_category_list: List[str],
    destination_url: Destination_url,
):
    """
    Post path for article categorizing.
    You MUST use post_term() before using post_category().
        `pathLIST`: list of str,
    if you want to post path = "Indian Treatises/Madyamika/The way of the bodhisattvas"
        => post_category(["Indian Treatises"])
        => post_category(["Indian Treatises", "Madyamika"])
        => post_category(["Indian Treatises", "Madyamika", "The way of the bodhisattvas"])
    """
    url = destination_url.value + "api/category"
    category = {
        "sharedTitle": list(map(lambda x: x["name"], en_category_list))[-1],
        "path": list(map(lambda x: x["name"], en_category_list)),
        "enDesc": list(map(lambda x: x["enDesc"], en_category_list))[-1],
        "heDesc": list(map(lambda x: x["heDesc"], bo_category_list))[-1],
        "enShortDesc": list(map(lambda x: x["enShortDesc"], en_category_list))[-1],
        "heShortDesc": list(map(lambda x: x["heShortDesc"], bo_category_list))[-1],
    }
    input_json = json.dumps(category)
    values = {"json": input_json, "apikey": PECHA_API_KEY}

    data = urlencode(values)
    binary_data = data.encode("ascii")
    req = Request(url, binary_data, headers=headers)
    category_name = list(map(lambda x: x["name"], en_category_list))[-1]
    try:
        response = urlopen(req)
        res = response.read().decode("utf-8")
        if "error" not in res:
            log_info(text_info_logger, f"Uploaded: {category_name}")
            return {"status": True}
        elif "already exists" in res:
            log_info(text_info_logger, f"Category already exists: {category_name}")
            return {"status": True}
        return {"status": True}
    except HTTPError as e:
        # error_message = e.read().decode("utf-8")
        log_error(text_error_logger, f"HTTPError while posting category: {e.code}")

        return {"status": False}

    except Exception as e:
        log_error(
            text_error_logger, f"Unexpected error while posting category: {str(e)}"
        )
        return {"status": False}
