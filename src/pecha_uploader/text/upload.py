import json
import urllib
from typing import Dict, List
from urllib.error import HTTPError

from pecha_uploader.clear_unfinished_text import remove_texts_meta
from pecha_uploader.config import PECHA_API_KEY, headers, logger
from pecha_uploader.exceptions import APIError
from pecha_uploader.text.extract import get_text


def can_remove_index(
    text_index: str, text_title: str, destination_url: str
):
    """check if index can be removed"""

    texts = get_text(text_title, destination_url)
    if "error" not in texts:
        total_versions = len(texts["versions"])
    else:
        total_versions = 0

    if text_index != text_title:
        return False
    elif text_index == text_title and total_versions == 0:
        return True


def post_text(
    text_name: str,
    text_content: Dict,
    category_path: List,
    destination_url: str,
    text_index_key: str,
):

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
    url = destination_url + f"api/texts/{prepare_text}?count_after=1"

    values = {"json": text_input_json, "apikey": f"{PECHA_API_KEY}"}
    data = urllib.parse.urlencode(values)
    binary_data = data.encode("ascii")
    req = urllib.request.Request(url, binary_data, headers=headers)
    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        if "error" in res:
            if "Failed to parse sections for ref" in res:
                logger.warning(f"Text: Failed to parse sections for ref {text_name}")

            if can_remove_index(
                text_index_key, text_content["versionTitle"], destination_url
            ):
                remove_texts_meta(
                    {
                        "term": text_name,
                        "category": category_path,
                        "index": text_index_key,
                    },
                    destination_url,
                )
            raise APIError(f"Text : '{res}'")
        else:
            logger.info(f"UPLOADED: Text '{text_content['versionTitle']}'")

    except HTTPError as e:
        error_message = (
            f"Text: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        )
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"Text: {e}"
        raise Exception(error_message)
