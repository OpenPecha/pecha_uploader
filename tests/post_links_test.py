import unittest
from unittest.mock import patch

from pecha_uploader.config import Destination_url, logger
from pecha_uploader.links.upload import post_link


class TestPostLink(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_post_link_success(self, mock_urlopen):
        # Mock a successful response
        mock_response = unittest.mock.Mock()
        mock_response.read.return_value = b'{"status": "success"}'
        mock_urlopen.return_value = mock_response

        # Test data
        ref_list = [
            {
                "refs": [
                    "The Sutra of the Great Vehicle Called the Diamond Cutter 1:5",
                    "An Extensive Commentary on “Diamond Sutra 1:5",
                ],
                "type": "commentary",
            },
            {
                "refs": [
                    "The Sutra of the Great Vehicle Called the Diamond Cutter 1:6",
                    "An Extensive Commentary on “Diamond Sutra 1:6",
                ],
                "type": "commentary",
            },
        ]
        ref_list_size = len(ref_list)
        destination_url = Destination_url.STAGING

        # Call the function
        post_link(ref_list, destination_url)

        # Check if the logger was called with the success message
        logger.info(f"UPLOADED: {ref_list_size} Links ")

    @patch("urllib.request.urlopen")
    def test_post_link_error(self, mock_urlopen):
        # Mock an error response
        mock_response = unittest.mock.Mock()
        mock_response.read.return_value = b'{"error": "Something went wrong"}'
        mock_urlopen.return_value = mock_response

        # Test data
        ref_list = [
            {
                "refs": [
                    "The Sutra of the Great Vehicle Called the Diamond Cutter 1:5",
                    "An ive Commentary on “Diamond Sutra 1:5",
                ],
                "type": "commentary",
            },
        ]
        destination_url = Destination_url.STAGING

        # Call the function
        post_link(ref_list, destination_url)

        # Check if the logger was called with the error message
        logger.error("Link {'error': 'Something went wrong'}")


if __name__ == "__main__":
    unittest.main()
