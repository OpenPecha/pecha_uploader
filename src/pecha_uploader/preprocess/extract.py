import urllib
from urllib.error import HTTPError

from pecha_uploader.config import baseURL, headers


def get_term(term: str):
    """
    Get term values for variable `term_str`.
        `term`: str, term name
    """
    url = baseURL + "api/terms/" + urllib.parse.quote(term)
    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req)
        print(response.read().decode("utf-8"))
    except HTTPError as e:
        print("Error code: ", e.code)
        print(e.read().decode("utf-8"))
