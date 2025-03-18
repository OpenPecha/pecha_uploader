import json
import urllib
from typing import Dict, List
from urllib.error import HTTPError

from pecha_uploader.clear_unfinished_text import remove_texts_meta
from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers, logger
from pecha_uploader.exceptions import APIError  # Import the custom exception


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

    print("index_str>>>>>>>>>>>>>>>>>>>>", index_str)
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
    category_path = list(map(lambda x: x["name"], category_list))
    index = {"title": "", "categories": [], "schema": {}}
    index["title"] = index_str
    index["categories"] = category_path
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
            logger.error(f"{res}")
            remove_texts_meta(
                {"term": index_str, "category": category_path}, destination_url
            )
            raise APIError(f"{res}")

        logger.info(f"UPLOADED: Index '{index_str}'")

    except HTTPError as e:
        error_message = f"HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        logger.error(f"index : {error_message}")
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"{e}"
        logger.error(f"index : {error_message}")
        raise Exception(error_message)
