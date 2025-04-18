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

    def get_link(self, link_name: str, destination_url: Destination_url, with_text=1):
        """
        Get links for article/section/row `link_name`
            `link_name`: str, article/section/row name
                article  => link_name = "The way of the bodhisattvas"
                section  => link_name = "The way of the bodhisattvas.1"
                sections => link_name = "The way of the bodhisattvas.1-2"
                row      => link_name = "The way of the bodhisattvas.1:1"
                rows     => link_name = "The way of the bodhisattvas.1:1-3"
        """
        link_name = link_name.replace(" ", "_")
        link_url = ""
        for c in link_name:
            if ord(c) > 128:
                link_url += urllib.parse.quote(c)
            else:
                link_url += c
        url = destination_url.value + f"api/links/{link_url}?with_text={with_text}"
        req = urllib.request.Request(url, method="GET", headers=headers)
        try:
            response = urllib.request.urlopen(req)  # noqa
            res = response.read().decode("utf-8")
            return res

        except HTTPError as e:
            error_message = f"Link extract: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
            raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

        except Exception as e:
            error_message = f"Link extract: {e}"
            raise Exception(error_message)

    def post_link(self, ref_list: Union[List, Dict], destination_url: Destination_url):
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
