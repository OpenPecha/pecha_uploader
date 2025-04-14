import io
import json
import unittest
import urllib
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url
from pecha_uploader.links.upload import post_link


class TestLinkUpload(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST

        # Sample link data as a list
        self.link_list = [
            {
                "refs": [
                    "The Way of the Bodhisattva.1.1",
                    "Commentary on Bodhisattva.2.3",
                ],
                "type": "commentary",
            },
            {
                "refs": [
                    "The Way of the Bodhisattva.2.4",
                    "Commentary on Bodhisattva.2.5-10",
                ],
                "type": "commentary",
            },
        ]

        # Sample link data as a dict
        self.link_dict = {
            "refs": ["The Way of the Bodhisattva.3.2", "Commentary on Bodhisattva.1.2"],
            "type": "quotation",
        }

        # URL for the API request
        self.url = self.destination_url.value + "api/links/"

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_link_list_success(self, mock_request, mock_urlopen):
        """Test successful link upload with a list of links"""
        # Setup mock response
        mock_response = MagicMock()
        expected_response = {"status": "success"}
        mock_response.read.return_value = json.dumps(expected_response).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function with list
        post_link(self.link_list, self.destination_url)

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

        # Check link data was sent correctly
        self.assertEqual(sent_json, self.link_list)

        # Check apikey was included
        self.assertIn("apikey", parsed_data)

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_link_dict_success(self, mock_request, mock_urlopen):
        """Test successful link upload with a single link as dict"""
        # Setup mock response
        mock_response = MagicMock()
        expected_response = {"status": "success"}
        mock_response.read.return_value = json.dumps(expected_response).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function with dict
        post_link(self.link_dict, self.destination_url)

        # Assertions
        mock_request.assert_called_once()
        mock_urlopen.assert_called_once()

        # Verify the request parameters
        request_args, request_kwargs = mock_request.call_args

        # Check URL is correctly formed
        self.assertEqual(request_args[0], self.url)

        # Convert binary data back to string and parse
        data_str = request_args[1].decode("ascii")
        parsed_data = urllib.parse.parse_qs(data_str)

        # Check that 'json' parameter exists
        self.assertIn("json", parsed_data)

        # Parse the JSON data sent
        sent_json = json.loads(parsed_data["json"][0])

        # Check link data was sent correctly
        self.assertEqual(sent_json, self.link_dict)

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_link_http_error(self, mock_request, mock_urlopen):
        """Test HTTP error handling"""
        # Setup mock HTTP error
        error_message = "Invalid link format"
        mock_fp = io.BytesIO(error_message.encode("utf-8"))
        http_error = HTTPError(self.url, 400, "Bad Request", {}, mock_fp)
        mock_urlopen.side_effect = http_error

        # Test that HTTP error is handled properly
        with self.assertRaises(HTTPError) as context:
            post_link(self.link_list, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Link: HTTP Error 400 occurred", str(context.exception))

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_link_general_exception(self, mock_request, mock_urlopen):
        """Test general exception handling"""
        # Setup general exception
        mock_urlopen.side_effect = Exception("Connection timeout")

        # Test that general exception is handled properly
        with self.assertRaises(Exception) as context:
            post_link(self.link_list, self.destination_url)

        # Verify the error message contains our custom message
        self.assertIn("Link: Connection timeout", str(context.exception))


if __name__ == "__main__":
    unittest.main()
