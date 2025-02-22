import json
import urllib
from typing import Dict
from urllib.error import HTTPError

from pecha_uploader.config import get_api_key, Destination_url, headers


def post_text(text_name: str, text_content: Dict, destination_url: Destination_url):

    """
    Post text to article `text_name`.
        `text_name`: str, article name,
        `text_content`: dict, text value
            text_content = {
            "versionTitle": "Your version title",
            "versionSource": "Version source url",
            "language": "en/he",
            "text": [
                [
                    "Paragraph 1 row 1",
                    "Paragraph 1 row 2",
                    ...
                ],
                [
                    "Paragraph 2 row 1",
                    "Paragraph 2 row 2",
                    ...
                ],
                ...
            ]
        }
    """
    text_input_json = json.dumps(text_content)
    # text_name = text_name.replace(" ", "_")

    prepare_text = urllib.parse.quote(text_name)

    url = destination_url.value + f"api/texts/{prepare_text}?count_after=1"

    values = {"json": text_input_json, "apikey": get_api_key()}
    data = urllib.parse.urlencode(values)
    binary_data = data.encode("ascii")
    req = urllib.request.Request(url, binary_data, headers=headers)
    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        if "error" in res:
            if "Failed to parse sections for ref" in res:
                return {"status": True}
            return {"status": False, "error": res}
        else:
            return {"status": True}

        return {"status": False, "error": res}
    except HTTPError as e:
        return {"status": False, "error": e}
