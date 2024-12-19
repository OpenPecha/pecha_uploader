import urllib
from urllib.error import HTTPError

from pecha_uploader.config import baseURL, headers


def get_category(category_name: str):
    """
    Check full category path for variable `category_name`.
        `category_name`: str, example: "Indian Treatises/Madyamika/The way of the bodhisattvas"
    """
    url = baseURL + "api/category/" + urllib.parse.quote(category_name)
    req = urllib.request.Request(url, method="GET", headers=headers)

    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        print(res)
        if "error" not in res:
            return {"status": True}
        elif "already exists" in res["error"]:
            return {"status": True}
        return {"status": False, "error": res}
    except HTTPError as e:
        print("[categories] Error code: ", e.code)
        print(e.read())
        return {"status": False, "error": res}
