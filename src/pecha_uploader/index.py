import json
import urllib
from typing import Dict, List
from urllib.error import HTTPError

from pecha_uploader.clear_unfinished_text import remove_texts_meta
from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers
from pecha_uploader.exceptions import APIError


class PechaIndex:
    def remove_index(self, index_key: str, destination_url: Destination_url):
        """
        index_key > index title
        """
        index_key = index_key.replace(" ", "_")
        url = destination_url.value + f"api/index/{index_key}"
        values = {"apikey": PECHA_API_KEY}
        data = urllib.parse.urlencode(values)
        binary_key = data.encode("ascii")
        headers["apiKey"] = PECHA_API_KEY
        req = urllib.request.Request(url, binary_key, method="DELETE", headers=headers)
        try:
            urllib.request.urlopen(req)
            # res = urllib.request.urlopen(req)

        except HTTPError as e:
            error_message = f"Index delete:HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"  # noqa
            raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

        except Exception as e:
            error_message = f"Index delete {e}"
            raise Exception(error_message)

    def upload_index(
        self,
        index_str: str,
        category_list: List[str],
        nodes: Dict,
        destination_url: Destination_url,
    ):
        """ "
        Post index value for article settings.
            `index`: str, article title,
            `catLIST`: list of str, category list (see upload_category() for example),
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
            if "error" in res:
                if "already exists." not in res:
                    remove_texts_meta(
                        {"term": index_str, "category": category_path}, destination_url
                    )
                    raise APIError(f"Index ({index_str}):  {res}")

        except HTTPError as e:
            error_message = (
                f"Index: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
            )
            raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

        except Exception as e:
            error_message = f" Index: {e}"
            raise Exception(error_message)
