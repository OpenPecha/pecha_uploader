import io
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pecha_uploader.config import Destination_url
from pecha_uploader.index.upload import post_index


class TestIndexUpload(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST

        # Sample index data
        self.index_str = "The Way of the Bodhisattva"

        # Sample category data
        self.category_list = [
            {"name": "Madhyamaka", "enDesc": "", "enShortDesc": "Madhyamaka treatises"},
            {
                "name": "The Way of the Bodhisattva",
                "enDesc": "",
                "enShortDesc": "The Way of the Bodhisattva treatises",
            },
        ]

        # Sample schema data
        self.nodes = {
            "nodeType": "JaggedArrayNode",
            "depth": 2,
            "titles": [
                {"lang": "en", "text": "The Way of the Bodhisattva", "primary": True},
                {"lang": "he", "text": "སྤྱོད་འཇུག", "primary": True},
            ],
            "key": "The Way of the Bodhisattva",
            "sectionNames": ["Chapter", "Verse"],
            "addressTypes": ["Integer", "Integer"],
        }

        # Expected URL
        self.url = (
            self.destination_url.value
            + "api/v2/raw/index/"
            + self.index_str.replace(" ", "_")
        )

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_index_success(self, mock_request, mock_urlopen):
        # Setup mock response
        mock_response = MagicMock()
        expected_response = {"status": "success"}
        mock_response.read.return_value = json.dumps(expected_response).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function
        post_index(self.index_str, self.category_list, self.nodes, self.destination_url)

        # Assertions
        mock_request.assert_called_once()
        mock_urlopen.assert_called_once()

        # Verify the URL was constructed correctly
        request_args, request_kwargs = mock_request.call_args
        self.assertEqual(request_args[0], self.url)

        # Verify the data was properly formatted
        binary_data = request_args[1]
        data_str = binary_data.decode("ascii")
        import urllib.parse

        parsed_data = urllib.parse.parse_qs(data_str)

        # Check that 'json' parameter exists
        self.assertIn("json", parsed_data)

        # Parse the JSON data sent
        sent_json = json.loads(parsed_data["json"][0])

        # Verify the content of the JSON
        self.assertEqual(sent_json["title"], self.index_str)
        self.assertEqual(
            sent_json["categories"], ["Madhyamaka", "The Way of the Bodhisattva"]
        )
        self.assertEqual(sent_json["schema"], self.nodes)

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_index_with_commentary(self, mock_request, mock_urlopen):
        # Modify category list to include commentary data
        commentary_category = self.category_list.copy()
        commentary_category[-1] = {
            "name": "The Way of the Bodhisattva",
            "enDesc": "",
            "enShortDesc": "The Way of the Bodhisattva treatises",
            "base_text_titles": ["Root Text"],
            "base_text_mapping": "many-to-one",
            "link": "Commentary",
        }

        # Setup mock response
        mock_response = MagicMock()
        expected_response = {"status": "success"}
        mock_response.read.return_value = json.dumps(expected_response).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function with commentary data
        post_index(
            self.index_str, commentary_category, self.nodes, self.destination_url
        )

        # Get the data sent to the request
        request_args, request_kwargs = mock_request.call_args
        binary_data = request_args[1]
        data_str = binary_data.decode("ascii")
        import urllib.parse

        parsed_data = urllib.parse.parse_qs(data_str)

        # Parse the JSON data sent
        sent_json = json.loads(parsed_data["json"][0])

        # Verify the commentary fields were added
        self.assertEqual(sent_json["base_text_titles"], ["Root Text"])
        self.assertEqual(sent_json["base_text_mapping"], "Exact")
        self.assertEqual(sent_json["collective_title"], self.index_str)
        self.assertEqual(sent_json["dependence"], "Commentary")

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_index_already_exists(self, mock_request, mock_urlopen):
        # Setup mock response with "already exists" message
        mock_response = MagicMock()
        error_message = {"error": f"Index {self.index_str} already exists."}
        mock_response.read.return_value = json.dumps(error_message).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Should not raise an exception for "already exists"
        post_index(self.index_str, self.category_list, self.nodes, self.destination_url)

        # Verify the request was made
        mock_request.assert_called_once()
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_index_http_error(self, mock_request, mock_urlopen):
        # Setup mock HTTP error
        error_message = "Index not found"
        mock_fp = io.BytesIO(error_message.encode("utf-8"))
        http_error = HTTPError(self.url, 404, "Not Found", {}, mock_fp)
        mock_urlopen.side_effect = http_error

        # Test that HTTP error is handled properly
        with self.assertRaises(HTTPError) as context:
            post_index(
                self.index_str, self.category_list, self.nodes, self.destination_url
            )

        # Verify the error message contains our custom message
        self.assertIn("Index: HTTP Error 404 occurred", str(context.exception))

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_post_index_general_exception(self, mock_request, mock_urlopen):
        # Setup general exception
        mock_urlopen.side_effect = Exception("Connection timeout")

        # Test that general exception is handled properly
        with self.assertRaises(Exception) as context:
            post_index(
                self.index_str, self.category_list, self.nodes, self.destination_url
            )

        # Verify the error message contains our custom message
        self.assertIn("Index: Connection timeout", str(context.exception))


if __name__ == "__main__":
    unittest.main()
