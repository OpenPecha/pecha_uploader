import json
from typing import List
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pecha_uploader.clear_unfinished_text import remove_texts_meta
from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers, logger
from pecha_uploader.exceptions import APIError


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
    category_path = list(map(lambda x: x["name"], en_category_list))
    category = {
        "sharedTitle": category_path[-1],
        "path": category_path,
        "enDesc": list(map(lambda x: x["enDesc"], en_category_list))[-1],
        "heDesc": list(map(lambda x: x["heDesc"], bo_category_list))[-1],
        "enShortDesc": list(map(lambda x: x["enShortDesc"], en_category_list))[-1],
        "heShortDesc": list(map(lambda x: x["heShortDesc"], bo_category_list))[-1],
    }
    # place root at top of TOC in pecha.org
    if category_path[-1] == "Root text":
        category["order"] = 1
    if category_path[-1] == "Commentaries":
        category["order"] = 2

    input_json = json.dumps(category)
    values = {"json": input_json, "apikey": PECHA_API_KEY}

    data = urlencode(values)
    binary_data = data.encode("ascii")
    req = Request(url, binary_data, headers=headers)
    category_name = category_path[-1]

    try:
        response = urlopen(req)
        res = response.read().decode("utf-8")
        if "error" not in res:
            logger.info(f"UPLOADED: Category '{category_name}'")
        elif "already exists" not in res and "error" in res:
            remove_texts_meta({"term": category_name}, destination_url)
            raise APIError(f"Category: {res}")

    except HTTPError as e:
        error_message = (
            f"Category: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        )
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"Category : {e}"
        raise Exception(error_message)
