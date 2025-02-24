import urllib
from urllib.error import HTTPError

from pecha_uploader.config import baseURL, headers, logger


def get_term(term: str):
    """
    Get term values for variable `term_str`.
        `term`: str, term name
    """
    url = baseURL + "api/terms/" + urllib.parse.quote(term)
    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req)  # noqa
        res = response.read().decode("utf-8")
        logger.info(f"term: {res}")
        return {"status": True}
    except HTTPError as e:
        error_message = e.read().decode("utf-8")
        logger.error(
            f"HTTPError while fetching term '{term}': {error_message}", exc_info=True
        )
        return {"status": False}

    except Exception as e:
        logger.exception(f"Unexpected error while fetching term '{term}': {str(e)}")
        return {"status": False}
