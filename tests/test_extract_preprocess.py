import io
import json
import unittest
import urllib
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url, headers
from pecha_uploader.preprocess.extract import get_term


class TestTermExtract(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST
        self.term_name = "Madhyamaka"
        self.encoded_term = urllib.parse.quote(self.term_name)
        self.url = self.destination_url.value + "api/terms/" + self.encoded_term

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_term_success(self, mock_request, mock_urlopen):
        # Setup mock response
        mock_response = MagicMock()
        expected_response = '{"name": "Madhyamaka", "titles": [{"text": "Madhyamaka", "lang": "en", "primary": true}, {"text": "དབུ་མ།", "lang": "he", "primary": true}]}'  # noqa
        mock_response.read.return_value = json.dumps(expected_response).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function
        result = get_term(self.term_name, self.destination_url)

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, expected_response)

        # Verify the URL was correctly formatted
        mock_request.assert_called_with(self.url, headers=headers)

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_term_http_error(self, mock_request, mock_urlopen):
        # Setup mock HTTP error
        error_message = "Term not found"
        mock_fp = io.BytesIO(error_message.encode("utf-8"))
        http_error = HTTPError(self.url, 404, "Not Found", {}, mock_fp)
        mock_urlopen.side_effect = http_error

        # Test that HTTP error is handled properly
        with self.assertRaises(HTTPError) as context:
            get_term(self.term_name, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Term: HTTP Error 404 occurred", str(context.exception))

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_term_general_exception(self, mock_request, mock_urlopen):
        # Setup general exception
        mock_urlopen.side_effect = Exception("Connection timeout")

        # Test that general exception is handled properly
        with self.assertRaises(Exception) as context:
            get_term(self.term_name, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Term: Connection timeout", str(context.exception))


if __name__ == "__main__":
    unittest.main()
