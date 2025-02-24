import json
import urllib
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers, logger


def post_term(term_en: str, term_bo: str, destination_url: Destination_url):
    """
    Post term for category in different language.
    You MUST post term before posting any category.
        `term_en`: str, primary `en` term (chinese),
        `term_bo`: str, primary `he` term (བོད་ཡིག)
    """
    url = destination_url.value + "api/terms/" + urllib.parse.quote(term_en)
    input_json = json.dumps(
        {
            "name": term_en,
            "titles": [
                {"text": term_en, "lang": "en", "primary": True},
                {"text": term_bo, "lang": "he", "primary": True},
            ],
        }
    )
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
        if (
            "error" in res
            and "A Term with the title" in res
            and "in it already exists" in res
        ):
            logger.warning(f"Term conflict for '{term_en}': {res}")
            return {"status": True}

        logger.info(f"Term '{term_en}' successfully posted")
        return {"status": True}

    except HTTPError as e:
        error_message = e.read().decode("utf-8")
        logger.error(
            f"HTTPError while posting term '{term_en}': {error_message}", exc_info=True
        )
        return {"status": False}

    except Exception as e:
        logger.exception(f"Unexpected error while posting term '{term_en}': {str(e)}")
        return {"status": False}
