import unittest
from unittest.mock import patch

from pecha_uploader.config import Destination_url
from pecha_uploader.pipeline import upload


class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Setup mock destination URL
        self.destination_url = Destination_url.TEST

        # Sample JSON data structure that the pipeline expects
        self.json_data = {
            "source": {
                "categories": [
                    {"name": "Madhyamaka", "enDesc": "", "enShortDesc": ""},
                    {
                        "name": "The Way of the Bodhisattva",
                        "base_text_titles": ["Root Text"],
                        "base_text_mapping": "many-to-one",
                        "link": "Commentary",
                    },
                ],
                "books": [
                    {
                        "title": "The Way of the Bodhisattva",
                        "language": "en",
                        "versionSource": "",
                        "completestatus": "done",
                        "content": [
                            [
                                "<1,4> Chapter 1, verse 1",
                                "<1,4><1,3> Chapter 1, verse 2",
                            ]
                        ],
                    }
                ],
            },
            "target": {
                "categories": [
                    {"name": "དབུ་མ།", "heDesc": "", "heShortDesc": ""},
                    {
                        "name": "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                        "base_text_titles": ["Root Text"],
                        "base_text_mapping": "many-to-one",
                        "link": "Commentary",
                    },
                ],
                "books": [
                    {
                        "title": "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                        "language": "bo",
                        "versionSource": "",
                        "completestatus": "done",
                        "content": [],
                    }
                ],
            },
        }

    @patch("pecha_uploader.pipeline.post_term")
    @patch("pecha_uploader.pipeline.post_category")
    @patch("pecha_uploader.pipeline.generate_schema")
    @patch("pecha_uploader.pipeline.post_index")
    @patch("pecha_uploader.pipeline.process_text")
    @patch("pecha_uploader.pipeline.is_commentary")
    @patch("pecha_uploader.pipeline.create_links")
    @patch("pecha_uploader.pipeline.add_links")
    def test_upload_with_root_text(
        self,
        mock_add_links,
        mock_create_links,
        mock_is_commentary,
        mock_process_text,
        mock_post_index,
        mock_generate_schema,
        mock_post_category,
        mock_post_term,
    ):
        """Test upload with a root text (not commentary)"""
        # Setup mocks
        mock_generate_schema.return_value = [{"schema": "mock_schema"}]
        mock_is_commentary.return_value = False  # Root text, not commentary

        # Call function
        upload(self.json_data, self.destination_url)

        # Verify functions were called correctly
        mock_create_links.assert_not_called()  # Should not be called for root text
        mock_add_links.assert_not_called()  # Should not be called for root text

    @patch("pecha_uploader.pipeline.post_term")
    @patch("pecha_uploader.pipeline.post_category")
    @patch("pecha_uploader.pipeline.generate_schema")
    @patch("pecha_uploader.pipeline.post_index")
    @patch("pecha_uploader.pipeline.process_text")
    @patch("pecha_uploader.pipeline.is_commentary")
    @patch("pecha_uploader.pipeline.create_links")
    @patch("pecha_uploader.pipeline.add_links")
    def test_upload_with_commentary_text(
        self,
        mock_add_links,
        mock_create_links,
        mock_is_commentary,
        mock_process_text,
        mock_post_index,
        mock_generate_schema,
        mock_post_category,
        mock_post_term,
    ):
        """Test upload with a commentary text"""
        # Setup mocks
        mock_generate_schema.return_value = [{"schema": "mock_schema"}]
        mock_is_commentary.return_value = True  # Commentary text

        # Create mock links data
        mock_links = [
            {
                "refs": ["Root Text 1:1", "The Way of the Bodhisattva 1"],
                "type": "commentary",
            },
            {
                "refs": ["Root Text 1:2", "The Way of the Bodhisattva 2"],
                "type": "commentary",
            },
        ]
        mock_create_links.return_value = mock_links

        # Call function
        upload(self.json_data, self.destination_url)

        # Verify functions were called correctly
        mock_create_links.assert_called_once_with(
            self.json_data
        )  # Should be called for commentary
        mock_add_links.assert_called_once_with(
            mock_links, self.destination_url
        )  # Should be called with the links

    @patch("pecha_uploader.pipeline.add_texts")
    def test_upload_exception_handling(self, mock_add_texts):
        """Test that exceptions in the upload process are caught and raised properly"""
        # Setup mock to raise exception
        error_message = "Test exception"
        mock_add_texts.side_effect = Exception(error_message)

        # Verify exception is raised with the same message
        with self.assertRaises(Exception) as context:
            upload(self.json_data, self.destination_url)

        self.assertIn(error_message, str(context.exception))


if __name__ == "__main__":
    unittest.main()
