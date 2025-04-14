import io
import json
import unittest
import urllib
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url
from pecha_uploader.preprocess.upload import post_term


class TestTermUpload(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST

        # Sample term data
        self.term_en = "Madhyamaka"
        self.term_bo = "དབུ་མ།"
        self.encoded_term = urllib.parse.quote(self.term_en)
        self.url = self.destination_url.value + "api/terms/" + self.encoded_term

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_term_success(self, mock_request, mock_urlopen):
        # Setup mock response
        mock_response = MagicMock()
        expected_response = {"update": {"status": "ok"}}
        mock_response.read.return_value = json.dumps(expected_response).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function
        post_term(self.term_en, self.term_bo, self.destination_url)

        # Assertions
        mock_request.assert_called_once()
        # Check that urlopen was called
        mock_urlopen.assert_called_once()

        # Verify the request parameters
        request_args, request_kwargs = mock_request.call_args

        # Check URL is correctly formed
        self.assertEqual(request_args[0], self.url)

        # Check method and headers
        self.assertEqual(request_kwargs["method"], "POST")
        self.assertIn("headers", request_kwargs)

        # Convert binary data back to string and parse
        data_str = request_args[1].decode("ascii")
        parsed_data = urllib.parse.parse_qs(data_str)

        # Check that 'json' parameter exists
        self.assertIn("json", parsed_data)

        # Parse the JSON data sent
        sent_json = json.loads(parsed_data["json"][0])

        # Check that the required fields are present
        self.assertEqual(sent_json["name"], self.term_en)
        self.assertIn("titles", sent_json)
        self.assertEqual(len(sent_json["titles"]), 2)

        # Check English title
        self.assertEqual(sent_json["titles"][0]["text"], self.term_en)
        self.assertEqual(sent_json["titles"][0]["lang"], "en")
        self.assertTrue(sent_json["titles"][0]["primary"])

        # Check Tibetan title
        self.assertEqual(sent_json["titles"][1]["text"], self.term_bo)
        self.assertEqual(sent_json["titles"][1]["lang"], "he")
        self.assertTrue(sent_json["titles"][1]["primary"])

        # Check other parameters
        self.assertIn("update", parsed_data)
        self.assertEqual(parsed_data["update"][0], "True")
        self.assertIn("apikey", parsed_data)

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_term_already_exists(self, mock_request, mock_urlopen):
        # Setup mock response with "already exists" error
        mock_response = MagicMock()
        error_message = {"error": f"Term already exists: {self.term_en}"}
        mock_response.read.return_value = json.dumps(error_message).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function - should not raise exception for "already exists"
        post_term(self.term_en, self.term_bo, self.destination_url)

        # Verify urlopen was called
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_term_http_error(self, mock_request, mock_urlopen):
        # Setup mock HTTP error
        error_message = "Term not found"
        mock_fp = io.BytesIO(error_message.encode("utf-8"))
        http_error = HTTPError(self.url, 404, "Not Found", {}, mock_fp)
        mock_urlopen.side_effect = http_error

        # Test that HTTP error is handled properly
        with self.assertRaises(HTTPError) as context:
            post_term(self.term_en, self.term_bo, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Term: HTTP Error 404 occurred", str(context.exception))

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_term_general_exception(self, mock_request, mock_urlopen):
        # Setup general exception
        mock_urlopen.side_effect = Exception("Connection timeout")

        # Test that general exception is handled properly
        with self.assertRaises(Exception) as context:
            post_term(self.term_en, self.term_bo, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Term: Connection timeout", str(context.exception))


if __name__ == "__main__":
    unittest.main()
