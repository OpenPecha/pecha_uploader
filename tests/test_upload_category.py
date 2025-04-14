import io
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pecha_uploader.category.upload import post_category
from pecha_uploader.config import Destination_url


class TestCategoryUpload(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST

        # Sample category data
        self.en_category_list = [
            {"name": "Madhyamaka", "enDesc": "", "enShortDesc": "Madhyamaka treatises"}
        ]

        self.bo_category_list = [
            {"name": "དབུ་མ།", "heDesc": "", "heShortDesc": "དབུ་མའི་གཞུང་སྣ་ཚོགས།"}
        ]

    @patch("pecha_uploader.category.upload.urlopen")
    @patch("pecha_uploader.category.upload.Request")
    def test_post_category_success(self, mock_request, mock_urlopen):
        # Setup mock response with expected data matching the actual API
        mock_response = MagicMock()
        expected_response = {"update": {"status": "ok"}}
        mock_response.read.return_value = json.dumps(expected_response).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Call the function
        post_category(
            self.en_category_list, self.bo_category_list, self.destination_url
        )

        # Assertions
        mock_request.assert_called_once()
        # Check that urlopen was called
        mock_urlopen.assert_called_once()

        # Verify the formatted category data
        # Get the call arguments
        request_args, request_kwargs = mock_request.call_args

        # The URL should be correctly formed
        self.assertEqual(request_args[0], self.destination_url.value + "api/category")

        # Convert binary data back to string and parse
        data_str = request_args[1].decode("ascii")
        import urllib.parse

        parsed_data = urllib.parse.parse_qs(data_str)

        # Check that 'json' parameter exists
        self.assertIn("json", parsed_data)

        # Parse the JSON data sent
        sent_json = json.loads(parsed_data["json"][0])
        print("Sent JSON:", sent_json)

        # Check that the required fields are present
        assert "" != self.en_category_list[0]["name"]
        assert "" != self.bo_category_list[0]["name"]
        self.assertIn("sharedTitle", sent_json)
        self.assertIn("path", sent_json)
        self.assertIn("enDesc", sent_json)
        self.assertIn("heDesc", sent_json)
        self.assertIn("enShortDesc", sent_json)
        self.assertIn("heShortDesc", sent_json)
        self.assertEqual(sent_json["sharedTitle"], self.en_category_list[0]["name"])

        # Verify the API response was read
        mock_response.read.assert_called_once()

        # Verify the response matches what we expect
        response_value = mock_response.read.return_value.decode("utf-8")
        self.assertEqual(response_value, json.dumps(expected_response))

    @patch("pecha_uploader.category.upload.urlopen")
    @patch("pecha_uploader.category.upload.Request")
    def test_post_category_already_exists(self, mock_request, mock_urlopen):
        # Setup mock response with "already exists" error
        mock_response = MagicMock()
        category_name = self.en_category_list[0]["name"]
        error_message = {"error": f"Category {category_name} already exists."}
        mock_response.read.return_value = json.dumps(error_message).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Instead of assertRaises, test that the function runs without raising an exception
        # and logs the already exists message
        with patch("pecha_uploader.category.upload.logger") as mock_logger:
            # Call the function - this should NOT raise an exception for "already exists"
            post_category(
                self.en_category_list, self.bo_category_list, self.destination_url
            )

            # No need to check remove_texts_meta since it's not called for "already exists"
            mock_logger.error.assert_called_once_with(
                f"Category: {error_message['error']}"
            )

    @patch("pecha_uploader.category.upload.urlopen")
    @patch("pecha_uploader.category.upload.Request")
    def test_post_category_http_error(self, mock_request, mock_urlopen):
        # Setup mock HTTP error
        error_message = "Category not found"
        mock_fp = io.BytesIO(error_message.encode("utf-8"))
        http_error = HTTPError(
            self.destination_url.value + "api/category", 404, "Not Found", {}, mock_fp
        )
        mock_urlopen.side_effect = http_error

        # Test that HTTP error is handled properly
        with self.assertRaises(HTTPError) as context:
            post_category(
                self.en_category_list, self.bo_category_list, self.destination_url
            )

        # Verify the error message contains our custom message
        self.assertIn("Category: HTTP Error 404 occurred", str(context.exception))

    @patch("pecha_uploader.category.upload.urlopen")
    @patch("pecha_uploader.category.upload.Request")
    def test_post_category_api_error(self, mock_request, mock_urlopen):
        # Setup mock response with API error
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"error": "Invalid category"}
        ).encode("utf-8")
        mock_urlopen.return_value = mock_response

        # Mock the remove_texts_meta function to avoid side effects
        with patch("pecha_uploader.category.upload.remove_texts_meta") as mock_remove:
            # Test that general exception is thrown (not APIError directly)
            with self.assertRaises(Exception) as context:
                post_category(
                    self.en_category_list, self.bo_category_list, self.destination_url
                )

            # Verify remove_texts_meta was called
            mock_remove.assert_called_once()

            # Verify the error message contains our custom message
            self.assertIn("Category :", str(context.exception))
            self.assertIn("Invalid category", str(context.exception))

    @patch("pecha_uploader.category.upload.urlopen")
    @patch("pecha_uploader.category.upload.Request")
    def test_post_category_general_exception(self, mock_request, mock_urlopen):
        # Setup general exception
        mock_urlopen.side_effect = Exception("Connection timeout")

        # Test that general exception is handled properly
        with self.assertRaises(Exception) as context:
            post_category(
                self.en_category_list, self.bo_category_list, self.destination_url
            )

        # Verify the error message contains our custom message
        self.assertIn("Category : Connection timeout", str(context.exception))


if __name__ == "__main__":
    unittest.main()
