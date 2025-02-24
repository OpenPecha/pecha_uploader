import urllib
from urllib.error import HTTPError

from pecha_uploader.config import baseURL, headers, logger


def get_category(category_name: str):
    """
    Check full category path for variable `category_name`.
        `category_name`: str, example: "Indian Treatises/Madyamika/The way of the bodhisattvas"
    """
    url = baseURL + "api/category/" + urllib.parse.quote(category_name)
    req = urllib.request.Request(url, method="GET", headers=headers)

    try:
        response = urllib.request.urlopen(req)
        res = response.read().decode("utf-8")
        if "error" not in res:
            logger.info(f"Category found: {category_name}")
            return {"status": True}
        elif "already exists" in res["error"]:
            logger.info(f"Category already exists: {category_name}")
            return {"status": True}
        logger.error(f"Category check failed: {res}")
        return {"status": False}
    except HTTPError as e:
        error_message = e.read().decode("utf-8")
        logger.error(
            f"HTTPError while fetching category: {error_message}", exc_info=True
        )
        return {"status": False, "error": error_message}

    except Exception as e:
        logger.exception(f"Unexpected error while fetching category: {str(e)}")
        return {"status": False}
