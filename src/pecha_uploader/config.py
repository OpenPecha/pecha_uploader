import os

PECHA_API_KEY = os.getenv("PECHA_API_KEY")
if not PECHA_API_KEY:
    raise ValueError("Please set PECHA_API_KEY environment variable")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"  # noqa
}
BASEPATH = os.path.dirname(os.path.abspath(__file__))  # path to `Pecha.org/tools`

# baseURL = "https://staging.pecha.org/"
baseURL = "http://127.0.0.1:8000/"
