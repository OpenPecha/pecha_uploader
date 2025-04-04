import json
import urllib
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers
from pecha_uploader.exceptions import APIError


def post_term(term_en: str, term_bo: str, destination_url: Destination_url):
    """
    Post term for category in different language.
    You MUST post term before posting any category.
        `term_en`: str, primary `en` term (chinese),
        `term_bo`: str, primary `he` term (བོད་ཡིག)
    """
    url = destination_url.value + "api/terms/" + urllib.parse.quote(term_en)
    payload = {
        "name": term_en,
        "titles": [
            {"text": term_en, "lang": "en", "primary": True},
            {"text": term_bo, "lang": "he", "primary": True},
        ],
    }
    input_json = json.dumps(payload)
    values = {
        "json": input_json,
        "apikey": PECHA_API_KEY,
        "update": True,
    }
    data = urllib.parse.urlencode(values)
    binary_data = data.encode("ascii")
    req = urllib.request.Request(url, binary_data, method="POST", headers=headers)
    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        # term conflict
        if "error" in res:
            if "Term already exists" not in res:
                raise APIError(
                    f"Failed to create category terms:English term: '{term_en}', Tibetan term: '{term_bo}' because {res}"  # noqa
                )

    except HTTPError as e:
        error_message = (
            f"Term: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        )
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"Term: {e}"
        raise Exception(error_message)
