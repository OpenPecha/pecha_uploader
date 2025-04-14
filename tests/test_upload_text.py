import io
import json
import unittest
import urllib
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url
from pecha_uploader.text.upload import post_text


class TestTextUpload(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST

        # Sample text data
        self.text_name = "The Way of the Bodhisattva"
        self.text_index_key = "The Way of the Bodhisattva"
        self.category_path = ["Madhyamaka", "Root", "The Way of the Bodhisattva"]

        # Prepare sample text content
        self.text_content = {
            "versionTitle": "The Way of the Bodhisattva",
            "versionSource": "https://example.com/source",
            "language": "en",
            "text": [
                ["Paragraph 1 row 1", "Paragraph 1 row 2"],
                ["Paragraph 2 row 1", "Paragraph 2 row 2"],
            ],
        }

        # URL for the API request
        self.prepare_text = urllib.parse.quote(self.text_name)
        self.url = (
            self.destination_url.value + f"api/texts/{self.prepare_text}?count_after=1"
        )

    @patch("pecha_uploader.text.upload.urllib.request.urlopen")
    @patch("pecha_uploader.text.upload.urllib.request.Request")
    @patch("pecha_uploader.text.upload.logger")
    def test_post_text_success(self, mock_logger, mock_request, mock_urlopen):
        """Test successful text upload"""
        # Setup mock response
        mock_response = MagicMock()
        expected_response = {"status": "success"}
        mock_response.read.return_value = json.dumps(expected_response).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call function
        post_text(
            self.text_name,
            self.text_content,
            self.category_path,
            self.destination_url,
            self.text_index_key,
        )

        # Assertions
        mock_request.assert_called_once()
        mock_urlopen.assert_called_once()

        # Verify the request parameters
        request_args, request_kwargs = mock_request.call_args

        # Check URL is correctly formed
        self.assertEqual(request_args[0], self.url)

        # Check headers
        self.assertIn("headers", request_kwargs)

        # Convert binary data back to string and parse
        data_str = request_args[1].decode("ascii")
        parsed_data = urllib.parse.parse_qs(data_str)

        # Check that 'json' parameter exists
        self.assertIn("json", parsed_data)

        # Parse the JSON data sent
        sent_json = json.loads(parsed_data["json"][0])

        # Check text content was sent correctly
        self.assertEqual(sent_json["versionTitle"], self.text_content["versionTitle"])
        self.assertEqual(sent_json["versionSource"], self.text_content["versionSource"])
        self.assertEqual(sent_json["language"], self.text_content["language"])
        self.assertEqual(sent_json["text"], self.text_content["text"])

        # Check log message
        mock_logger.info.assert_called_once_with(
            f"UPLOADED: Text '{self.text_content['versionTitle']}'"
        )

    @patch("pecha_uploader.text.upload.urllib.request.urlopen")
    @patch("pecha_uploader.text.upload.urllib.request.Request")
    @patch("pecha_uploader.text.upload.can_remove_index")
    @patch("pecha_uploader.text.upload.remove_texts_meta")
    @patch("pecha_uploader.text.upload.logger")
    def test_post_text_failed_to_parse_sections(
        self,
        mock_logger,
        mock_remove_texts_meta,
        mock_can_remove_index,
        mock_request,
        mock_urlopen,
    ):
        """Test 'Failed to parse sections' error"""
        # Setup mock response with parse error
        mock_response = MagicMock()
        error_message = {"error": f"Failed to parse sections for ref {self.text_name}"}
        mock_response.read.return_value = json.dumps(error_message).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Set can_remove_index to return True
        mock_can_remove_index.return_value = True

        # Test Exception is raised (not APIError, since it's wrapped in a general Exception)
        with self.assertRaises(Exception) as context:
            post_text(
                self.text_name,
                self.text_content,
                self.category_path,
                self.destination_url,
                self.text_index_key,
            )

        # Verify logger warning
        mock_logger.warning.assert_called_once_with(
            f"Text: Failed to parse sections for ref {self.text_name}"
        )

        # Verify can_remove_index was called
        mock_can_remove_index.assert_called_once_with(
            self.text_index_key, self.text_content["versionTitle"], self.destination_url
        )

        # Verify remove_texts_meta was called
        mock_remove_texts_meta.assert_called_once_with(
            {
                "term": self.text_name,
                "category": self.category_path,
                "index": self.text_index_key,
            },
            self.destination_url,
        )

        # Verify error message contains original APIError
        self.assertIn(
            f"Text: Text : '{json.dumps(error_message)}'", str(context.exception)
        )

    @patch("pecha_uploader.text.upload.urllib.request.urlopen")
    @patch("pecha_uploader.text.upload.urllib.request.Request")
    def test_post_text_http_error(self, mock_request, mock_urlopen):
        """Test HTTP error handling"""
        # Setup mock HTTP error
        error_message = "Text not found"
        mock_fp = io.BytesIO(error_message.encode("utf-8"))
        http_error = HTTPError(self.url, 404, "Not Found", {}, mock_fp)
        mock_urlopen.side_effect = http_error

        # Test that HTTP error is handled properly
        with self.assertRaises(HTTPError) as context:
            post_text(
                self.text_name,
                self.text_content,
                self.category_path,
                self.destination_url,
                self.text_index_key,
            )

        # Verify the error message contains our custom message
        self.assertIn("Text: HTTP Error 404 occurred", str(context.exception))

    @patch("pecha_uploader.text.upload.urllib.request.urlopen")
    @patch("pecha_uploader.text.upload.urllib.request.Request")
    def test_post_text_general_exception(self, mock_request, mock_urlopen):
        """Test general exception handling"""
        # Setup general exception
        mock_urlopen.side_effect = Exception("Connection timeout")

        # Test that general exception is handled properly
        with self.assertRaises(Exception) as context:
            post_text(
                self.text_name,
                self.text_content,
                self.category_path,
                self.destination_url,
                self.text_index_key,
            )

        # Verify the error message contains our custom message
        self.assertIn("Text: Connection timeout", str(context.exception))


if __name__ == "__main__":
    unittest.main()
