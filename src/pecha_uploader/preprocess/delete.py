import urllib.parse
import urllib.request
from urllib.error import HTTPError

from pecha_uploader.config import PECHA_API_KEY, Destination_url, headers


def remove_term(term_title: str, destination_url: Destination_url):
    """
    Remove a term from the API.
    `term_title`: The title of the term to remove.
    """
    encode_title = urllib.parse.quote(term_title)
    url = destination_url.value + f"api/terms/{encode_title}"

    values = {"apikey": PECHA_API_KEY}  # Must be sent as form data
    data = urllib.parse.urlencode(values).encode(
        "ascii"
    )  # Convert to form-encoded bytes
    headers["apiKey"] = PECHA_API_KEY
    req = urllib.request.Request(url, data=data, method="DELETE", headers=headers)
    try:
        response = urllib.request.urlopen(req)
        response.read().decode("utf-8")
    except HTTPError as e:
        error_message = (
            f"Term delete: HTTP Error {e.code} occurred: {e.read().decode('utf-8')}"
        )
        raise HTTPError(e.url, e.code, error_message, e.headers, e.fp)

    except Exception as e:
        error_message = f"Term delete: {e}"

        raise Exception(error_message)
