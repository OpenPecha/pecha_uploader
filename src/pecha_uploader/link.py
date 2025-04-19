import json
import re
import urllib.parse
import urllib.request
from typing import Dict, List, Union
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers


class PechaLink:
    def remove_links(self, text_title: str, destination_url: Destination_url):
        """
        text_title > Reference link of text. e.g Prayer 1:1 or Prayer 1:1-2
        """
        # remove section range number from text title. e.g Prayer 1:1, Prayer 1:1-2
        pattern = r"\s\d+:\d+(-\d+)?"
        clean_title = re.sub(pattern, "", text_title)

        ref = clean_title.replace(" ", "_")
        url = destination_url.value + f"api/links/{ref}"
        values = {"apikey": PECHA_API_KEY}
        data = urllib.parse.urlencode(values)
        binary_key = data.encode("ascii")
        req = urllib.request.Request(url, binary_key, method="DELETE", headers=headers)
        try:
            urllib.request.urlopen(req)
            # response = urllib.request.urlopen(req)

        except HTTPError as e:
            error_message = (
                f"Link delete: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
            )
            raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

        except Exception as e:
            error_message = f"Link delete: {e}"
            raise Exception(error_message)

    def upload_links(
        self, ref_list: Union[List, Dict], destination_url: Destination_url
    ):
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
        url = destination_url.value + "api/links/"
        input_json_link = json.dumps(ref_list)

        values = {"json": input_json_link, "apikey": PECHA_API_KEY}
        data = urllib.parse.urlencode(values)
        binary_data = data.encode("ascii")
        req = urllib.request.Request(url, binary_data, headers=headers)

        try:
            response = urllib.request.urlopen(req)
            response.read().decode("utf-8")

        except HTTPError as e:
            error_message = (
                f"Link: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
            )
            raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

        except Exception as e:
            error_message = f"Link: {e}"

            raise Exception(error_message)
