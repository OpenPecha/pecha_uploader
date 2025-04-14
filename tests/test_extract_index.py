import io
import unittest
import urllib.request
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url
from pecha_uploader.index.extract import get_index


class TestIndexExtract(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST
        self.index_name = "The Way of the Bodhisattva"
        self.encoded_index = urllib.parse.quote(self.index_name)
        self.url = self.destination_url.value + "api/v2/raw/index/" + self.encoded_index

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_index_success(self, mock_request, mock_urlopen):
        # Setup mock response
        mock_response = MagicMock()
        json_data = '{"title": "The Way of the Bodhisattva ", "heTitle": "སྤྱོད་འཇུག", "categories": ["Madhyamaka", "The Way of the Bodhisattva"], "schema": {"nodes": [{"titles": [], "nodeType": "JaggedArrayNode"}]}}'  # noqa
        mock_response.read.return_value = json_data.encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function
        result = get_index(self.index_name, self.destination_url)

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, json_data)

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_index_http_error(self, mock_request, mock_urlopen):
        # Setup mock HTTP error
        error_message = "Index not found"
        mock_fp = io.BytesIO(error_message.encode("utf-8"))
        http_error = HTTPError(self.url, 404, "Not Found", {}, mock_fp)
        mock_urlopen.side_effect = http_error

        # Test that HTTP error is handled properly
        with self.assertRaises(HTTPError) as context:
            get_index(self.index_name, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Index extract: HTTP Error 404 occurred", str(context.exception))

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_index_general_exception(self, mock_request, mock_urlopen):
        # Setup general exception
        mock_urlopen.side_effect = Exception("Connection timeout")

        # Test that general exception is handled properly
        with self.assertRaises(Exception) as context:
            get_index(self.index_name, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Index extract: Connection timeout", str(context.exception))


if __name__ == "__main__":
    unittest.main()
