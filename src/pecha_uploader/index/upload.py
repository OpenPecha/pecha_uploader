import json
import urllib
from typing import Dict, List
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, baseURL, headers


def post_index(index: str, category_list: List[str], nodes: Dict):
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
    url = baseURL + "api/v2/raw/index/" + urllib.parse.quote(index.replace(" ", "_"))

    # "titles" : titleLIST,
    # "key" : index,
    # "nodeType" : "JaggedArrayNode",
    # # "lengths" : [4, 50],
    # "depth" : 2,
    # "sections" : ["Chapter", "Verse"],
    # "addressTypes" : ["Integer", "Integer"],

    index = {"title": "", "categories": [], "schema": {}}
    index["title"] = index
    index["categories"] = list(map(lambda x: x["name"], category_list))
    index["schema"] = nodes

    # if text is commentary
    if "base_text_mapping" in category_list[-1].keys():
        index["base_text_titles"] = category_list[-1]["base_text_titles"]
        index["base_text_mapping"] = category_list[-1]["base_text_mapping"]
        index["collective_title"] = index
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
        print(res)
        if "error" in res and "already exists." not in res:
            return False
        return True
    except HTTPError as e:
        print("Error code: ", e.code)
        print(e.read())
        return False