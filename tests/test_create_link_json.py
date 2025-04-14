import unittest
from unittest.mock import ANY, patch

from pecha_uploader.links.create_ref_json import create_links


class TestCreateLinks(unittest.TestCase):
    def setUp(self):
        # Sample JSON data with source and target books
        self.json_text = {
            "source": {
                "categories": [
                    {"name": "Madhyamaka"},
                    {
                        "name": "The Way of the Bodhisattva",
                        "base_text_titles": ["Root Text"],
                        "base_text_mapping": "many-to-one",
                        "link": "Commentary",
                    },
                ],
                "books": [
                    {
                        "language": "en",
                        "content": [
                            "Chapter 1, verse 1 <1,1>",
                            "Chapter 1, verse 2 <1,2>",
                        ],
                    }
                ],
            },
            "target": {
                "books": [
                    {
                        "language": "bo",
                        "content": [
                            "བརྗོད་པ་ ༡ ཤླཽཀ་ ༡ <1,1>",
                            "བརྗོད་པ་ ༡ ཤླཽཀ་ ༢ <1,2>",
                        ],
                    }
                ],
            },
        }

        # Expected links that should be returned
        self.expected_links = [
            {
                "refs": ["Root Text 1:1", "The Way of the Bodhisattva 1"],
                "type": "commentary",
            },
            {
                "refs": ["Root Text 1:2", "The Way of the Bodhisattva 2"],
                "type": "commentary",
            },
        ]

    @patch("pecha_uploader.links.create_ref_json.generate_chapters")
    @patch("pecha_uploader.links.create_ref_json.link_mapper")
    def test_create_links_returns_correct_links(
        self, mock_link_mapper, mock_generate_chapters
    ):
        """Test that create_links returns the correct links structure"""
        # Setup mocks
        mock_chapters = {"The Way of the Bodhisattva": ["Chapter 1"]}
        mock_generate_chapters.return_value = mock_chapters
        mock_link_mapper.return_value = self.expected_links

        # Call the function
        result = create_links(self.json_text)

        # Check results
        self.assertEqual(result, self.expected_links)

        # Verify generate_chapters was called - using ANY for complex arguments
        # that are hard to predict exactly
        mock_generate_chapters.assert_any_call(
            ANY,  # First argument could be any dict
            ANY,  # Second argument could be any book structure
            ANY,  # Language
            "The Way of the Bodhisattva",  # Index key should match
        )

        # Verify link_mapper was called
        self.assertEqual(mock_link_mapper.call_count, 2)  # Once for each language

        # Verify first param of link_mapper is the key from our mock_chapters
        mock_link_mapper.assert_any_call(
            "The Way of the Bodhisattva",  # This should be exact
            ["Chapter 1"],  # From our mock_chapters
            self.json_text["source"]["categories"][-1],  # The category should match
        )

    def test_create_links_integration(self):
        """Integration test for create_links without mocking"""
        # Call the function with real implementation
        result = create_links(self.json_text)

        # Check that the result is a list of links
        self.assertIsInstance(result, list)

        # Each item in the list should be a dict with refs and type
        for link in result:
            self.assertIsInstance(link, dict)
            self.assertIn("refs", link)
            self.assertIn("type", link)
            self.assertEqual(link["type"], "commentary")

            # Each refs should be a list with 2 items
            self.assertIsInstance(link["refs"], list)
            self.assertEqual(len(link["refs"]), 2)

            # The first ref should start with the base text title
            self.assertTrue(link["refs"][0].startswith("Root Text"))

            # The second ref should start with the target text name
            self.assertTrue(link["refs"][1].startswith("The Way of the Bodhisattva"))


if __name__ == "__main__":
    unittest.main()
