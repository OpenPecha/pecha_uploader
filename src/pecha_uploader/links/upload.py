import json
import urllib
from typing import List
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, baseURL, headers


def post_link(ref_list: List[str], type_str: str):
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
    url = baseURL + "api/links/"
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
            return {"status": True, "res": res}
        elif "Link already exists" in res:
            return {"status": False, "res": res}
        return {"status": True, "res": res}
    except (HTTPError) as e:
        return {"status": False, "res": e.read()}
