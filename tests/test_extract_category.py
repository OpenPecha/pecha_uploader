import io
import unittest
import urllib.request
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pecha_uploader.category.extract import get_category
from pecha_uploader.config import Destination_url


class TestCategoryExtract(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST
        self.category_name = "Madhyamaka"
        self.encoded_category = urllib.parse.quote(self.category_name)
        self.url = self.destination_url.value + "api/category/" + self.encoded_category

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_category_success(self, mock_request, mock_urlopen):
        # Setup mock response
        mock_response = MagicMock()
        json_data = '{"lastPath": "Madhyamaka", "path": ["Madhyamaka"], "depth": 1, "enDesc": "", "heDesc": "", "enShortDesc": "Madhyamaka treatises", "heShortDesc": "དབུ་མའི་གཞུང་སྣ་ཚོགས།", "sharedTitle": "Madhyamaka"}'  # noqa
        mock_response.read.return_value = json_data.encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function
        result = get_category(self.category_name, self.destination_url)

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, json_data)

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_category_http_error(self, mock_request, mock_urlopen):
        # Setup mock HTTP error
        error_message = "Category not found"
        mock_fp = io.BytesIO(error_message.encode("utf-8"))
        http_error = HTTPError(self.url, 404, "Not Found", {}, mock_fp)
        mock_urlopen.side_effect = http_error

        # Test that HTTP error is handled properly
        with self.assertRaises(HTTPError) as context:
            get_category(self.category_name, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn(
            "Category extract: HTTP Error 404 occurred", str(context.exception)
        )

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_category_general_exception(self, mock_request, mock_urlopen):
        # Setup general exception
        mock_urlopen.side_effect = Exception("Connection timeout")

        # Test that general exception is handled properly
        with self.assertRaises(Exception) as context:
            get_category(self.category_name, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Category extract: Connection timeout", str(context.exception))


if __name__ == "__main__":
    unittest.main()
