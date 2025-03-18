import time
from typing import Dict, List, Union

from pecha_uploader.config import Destination_url, logger
from pecha_uploader.links.upload import post_link


def test_bulk_upload_link(ref_lists: Union[List, Dict], url: Destination_url):
    """this is test function for bulk upload link"""
    # Measure time for bulk upload
    start_bulk = time.time()
    post_link(ref_lists, url, len(ref_lists))
    end_bulk = time.time()
    bulk_time = end_bulk - start_bulk

    # Measure time for individual uploads
    start_individual = time.time()
    for ref in ref_lists:
        post_link(ref, url)  # type: ignore
    end_individual = time.time()
    individual_time = end_individual - start_individual

    logger.info("[TEST] Time taken by upload in bulk: %.4f seconds", bulk_time)
    logger.info("[TEST] Time taken by individual upload: %.4f seconds", individual_time)
    logger.info("[TEST] Time difference: %.4f seconds", individual_time - bulk_time)


if __name__ == "__main__":
    destination_url = Destination_url.STAGING
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
        {
            "refs": [
                "The Sutra of the Great Vehicle Called the Diamond Cutter 1:7",
                "An Extensive Commentary on “Diamond Sutra 1:7",
            ],
            "type": "commentary",
        },
        {
            "refs": [
                "The Sutra of the Great Vehicle Called the Diamond Cutter 1:8",
                "An Extensive Commentary on “Diamond Sutra 1:8",
            ],
            "type": "commentary",
        },
        {
            "refs": [
                "The Sutra of the Great Vehicle Called the Diamond Cutter 1:9",
                "An Extensive Commentary on “Diamond Sutra 1:9",
            ],
            "type": "commentary",
        },
        {
            "refs": [
                "The Sutra of the Great Vehicle Called the Diamond Cutter 1:10",
                "An Extensive Commentary on “Diamond Sutra 1:10",
            ],
            "type": "commentary",
        },
        {
            "refs": [
                "The Sutra of the Great Vehicle Called the Diamond Cutter 1:12",
                "An Extensive Commentary on “Diamond Sutra 1:11",
            ],
            "type": "commentary",
        },
        {
            "refs": [
                "The Sutra of the Great Vehicle Called the Diamond Cutter 1:15",
                "An Extensive Commentary on “Diamond Sutra 1:12-13",
            ],
            "type": "commentary",
        },
        {
            "refs": [
                "The Sutra of the Great Vehicle Called the Diamond Cutter 1:17",
                "An Extensive Commentary on “Diamond Sutra 1:14",
            ],
            "type": "commentary",
        },
        {
            "refs": [
                "The Sutra of the Great Vehicle Called the Diamond Cutter 1:20",
                "An Extensive Commentary on “Diamond Sutra 1:15",
            ],
            "type": "commentary",
        },
    ]
    test_bulk_upload_link(ref_list, destination_url)
