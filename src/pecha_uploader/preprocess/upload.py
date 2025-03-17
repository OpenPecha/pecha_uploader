import json
import urllib
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers, logger
from pecha_uploader.preprocess.delete import remove_term
from pecha_uploader.preprocess.extract import get_term


def check_term_conflict(term_en: str, term_bo: str, destination_url: Destination_url):

    term_en_result = get_term(term_en, destination_url)
    term_bo_result = get_term(term_bo, destination_url)

    if ("error" in term_en_result and "error" not in term_bo_result) or (
        "error" not in term_en_result and "error" in term_bo_result
    ):
        remove_term(term_en, destination_url)


def post_term(term_en: str, term_bo: str, destination_url: Destination_url):
    """
    Post term for category in different language.
    You MUST post term before posting any category.
        `term_en`: str, primary `en` term (English),
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
    values = {"json": input_json, "apikey": PECHA_API_KEY, "update": True}
    data = urllib.parse.urlencode(values)
    binary_data = data.encode("ascii")
    req = urllib.request.Request(url, binary_data, method="POST", headers=headers)
    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        # check_term_conflict(term_en, term_bo, destination_url)
        # term conflict
        if "error" in res:
            if "Term already exists" in res:
                logger.warning(f"Term : '{term_en}' already exists")
                return {"data": res}
            else:
                logger.error(f"ERROR: Term '{term_en}'")
                return {"error": res}
        else:
            logger.info(f"UPLOADED: Term '{term_en}'")
            return {"data": res}

    except HTTPError as e:
        error_message = f"HTTP Error {e.code} occurred: {e}"
        logger.error(f"Term : {error_message}")
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"{e}"
        logger.error(f"term : {error_message}")
        raise Exception(error_message)
