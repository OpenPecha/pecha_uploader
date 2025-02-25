import json
import urllib
from typing import Dict
from urllib.error import HTTPError

from pecha_uploader.config import text_info_logger  # <--- Import the Info Logger
from pecha_uploader.config import (
    PECHA_API_KEY,
    Destination_url,
    headers,
    log_error,
    log_info,
    text_error_logger,
)


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

    values = {"json": text_input_json, "apikey": f"{PECHA_API_KEY}"}
    data = urllib.parse.urlencode(values)
    binary_data = data.encode("ascii")
    req = urllib.request.Request(url, binary_data, headers=headers)
    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        if "error" in res:
            if "Failed to parse sections for ref" in res:
                return {"status": True}

            log_error(text_error_logger, f" '{text_name}': {res}")
            return {"status": False}
        else:
            log_info(text_info_logger, f"Uploaded:  '{text_name}'")
            return {"status": True}
    except HTTPError as e:
        # error_message = e.read().decode("utf-8")
        log_error(
            text_error_logger, f"HTTPError while posting text '{text_name}': {e.code}"
        )
        return {"status": False}

    except Exception as e:
        log_error(
            text_error_logger,
            f"Unexpected error while posting text '{text_name}': {str(e)}",
        )
        return {"status": False}
