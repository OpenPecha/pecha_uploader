import json
from typing import List
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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
            logger.info(f"Uploaded: {category_name}")
        elif "already exists" in res:
            logger.warning(f"Category already exists: {category_name}")
        else:
            logger.error(f"{res}")
            raise APIError(f"{res}")

    except HTTPError as e:
        error_message = f"HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        logger.error(f"category : {error_message}")
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"{e}"
        logger.error(f"category : {error_message}")
        raise Exception(error_message)
