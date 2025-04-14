import io
import json
import unittest
import urllib
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url
from pecha_uploader.text.extract import get_text


class TestTextExtract(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST

        # Sample text data
        self.text_name = "The Way of the Bodhisattva"
        self.encoded_text = urllib.parse.quote(self.text_name)
        self.url = f"{self.destination_url.value}api/texts/{self.encoded_text}?pad=0"

        # Sample response data
        self.expected_response = {
            "ref": "The Way of the Bodhisattva 1",
            "heRef": "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ། ༠༡",
            "isComplex": False,
            "text": [],
            "he": [
                "Ch-1༄། །བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ་བཞུགས་སོ། །",
                "༄༅༅། །རྒྱ་གར་སྐད་དུ། བོ་དྷི་སཏྭ་ཙརྱ་ཨ་བ་ཏཱ་ར།",
                "བོད་སྐད་དུ། བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                "སངས་རྒྱས་དང་བྱང་ཆུབ་སེམས་དཔའ་ཐམས་ཅད་ལ་ཕྱག་འཚལ་ལོ། །",
            ],
        }

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_get_text_success(self, mock_request, mock_urlopen):
        """Test successful text retrieval"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(self.expected_response).encode(
            "utf-8"
        )
        mock_urlopen.return_value = mock_response

        # Call the function
        result = get_text(self.text_name, self.destination_url)

        # Assertions
        mock_request.assert_called_once_with(
            self.url, method="GET", headers=unittest.mock.ANY
        )
        mock_urlopen.assert_called_once()

        # Verify response data was correctly parsed
        self.assertEqual(result, self.expected_response)
        self.assertEqual(result["ref"], self.expected_response["ref"])
        self.assertEqual(len(result["he"]), len(self.expected_response["he"]))
        self.assertEqual(len(result["text"]), len(self.expected_response["text"]))
        self.assertEqual(result["heRef"], self.expected_response["heRef"])

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    @patch("pecha_uploader.text.extract.logger")
    def test_get_text_http_error(self, mock_logger, mock_request, mock_urlopen):
        """Test HTTP error handling"""
        # Setup mock HTTP error
        error_message = "Text not found"
        mock_fp = io.BytesIO(error_message.encode("utf-8"))
        http_error = HTTPError(self.url, 404, "Not Found", {}, mock_fp)
        mock_urlopen.side_effect = http_error

        # Test that HTTP error is handled properly
        with self.assertRaises(HTTPError) as context:
            get_text(self.text_name, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("HTTP Error 404 occurred", str(context.exception))

        # Verify error was logged
        mock_logger.error.assert_called_once()

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    @patch("pecha_uploader.text.extract.logger")
    def test_get_text_general_exception(self, mock_logger, mock_request, mock_urlopen):
        """Test general exception handling"""
        # Setup general exception
        mock_urlopen.side_effect = Exception("Connection timeout")

        # Test that general exception is handled properly
        with self.assertRaises(Exception) as context:
            get_text(self.text_name, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Connection timeout", str(context.exception))

        # Verify error was logged
        mock_logger.error.assert_called_once_with("Connection timeout")


if __name__ == "__main__":
    unittest.main()
