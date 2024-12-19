import json
import urllib
from typing import List
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, baseURL, headers


def post_category(en_category_list: List[str], bo_category_list: List[str]):
    """
    Post path for article categorizing.
    You MUST use post_term() before using post_category().
        `pathLIST`: list of str,
    if you want to post path = "Indian Treatises/Madyamika/The way of the bodhisattvas"
        => post_category(["Indian Treatises"])
        => post_category(["Indian Treatises", "Madyamika"])
        => post_category(["Indian Treatises", "Madyamika", "The way of the bodhisattvas"])
    """
    url = baseURL + "api/category"
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

    data = urllib.parse.urlencode(values)
    binary_data = data.encode("ascii")
    req = urllib.request.Request(url, binary_data, headers=headers)

    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        print("categories response: ", res)
        if "error" not in res:
            return {"status": True}
        elif "already exists" in res:
            return {"status": True}
        return {"status": False, "error": res}
    except HTTPError as e:
        print("Error code: ", e)
        return {"status": False, "error": e}
