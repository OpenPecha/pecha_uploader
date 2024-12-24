import json
import urllib
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, baseURL, headers


def post_term(term_en: str, term_bo: str):
    """
    Post term for category in different language.
    You MUST post term before posting any category.
        `term_en`: str, primary `en` term (chinese),
        `term_bo`: str, primary `he` term (བོད་ཡིག)
    """
    url = baseURL + "api/terms/" + urllib.parse.quote(term_en)
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
            return {"status": True, "term_conflict": res}
        return {"status": True}
    except HTTPError as e:
        print("[term] Error code: ", e.code)
        return {"status": False, "error": e.read()}
