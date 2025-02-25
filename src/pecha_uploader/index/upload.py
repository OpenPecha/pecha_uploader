import json
import urllib
from typing import Dict, List
from urllib.error import HTTPError

from pecha_uploader.config import text_info_logger  # <--- Import the Info Logger
from pecha_uploader.config import (
    PECHA_API_KEY,
    Destination_url,
    headers,
    log_error,
    log_info,
    text_error_logger,
)


def post_index(
    index_str: str,
    category_list: List[str],
    nodes: Dict,
    destination_url: Destination_url,
):
    """ "
    Post index value for article settings.
        `index`: str, article title,
        `catLIST`: list of str, category list (see post_category() for example),
        `titleLIST`: list of json, title name in different language,
            titleLIST = {
                "lang": "en/he",
                "text": "Your en/he title",
                "primary": True (You must have a primary title for each language)
            }
    """
    url = (
        destination_url.value
        + "api/v2/raw/index/"
        + urllib.parse.quote(index_str.replace(" ", "_"))
    )

    # "titles" : titleLIST,
    # "key" : index,
    # "nodeType" : "JaggedArrayNode",
    # # "lengths" : [4, 50],
    # "depth" : 2,
    # "sections" : ["Chapter", "Verse"],
    # "addressTypes" : ["Integer", "Integer"],

    index = {"title": "", "categories": [], "schema": {}}
    index["title"] = index_str
    index["categories"] = list(map(lambda x: x["name"], category_list))
    index["schema"] = nodes

    # if text is commentary
    if "base_text_mapping" in category_list[-1].keys():
        index["base_text_titles"] = category_list[-1]["base_text_titles"]
        index["base_text_mapping"] = category_list[-1]["base_text_mapping"]
        index["collective_title"] = index_str
        index["dependence"] = category_list[-1]["link"]

    input_json = json.dumps(index, indent=4, ensure_ascii=False)

    values = {
        "json": input_json,
        "apikey": PECHA_API_KEY,
    }
    data = urllib.parse.urlencode(values)
    binary_data = data.encode("ascii")
    req = urllib.request.Request(url, binary_data, headers=headers)
    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        if "error" in res and "already exists." not in res:
            log_error(text_error_logger, f"API error response: {res}")
            return {"status": False}

        log_info(text_info_logger, f"Index uploaded: {index_str}")
        return {"status": True}

    except HTTPError as e:
        error_message = e.read().decode("utf-8")
        log_error(text_error_logger, f"HTTPError while posting index: {error_message}")
        return {"status": False}

    except Exception as e:
        log_error(text_error_logger, f"Unexpected error while posting index: {str(e)}")
        return {"status": False}
