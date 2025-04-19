"""
This module processes text files, parses JSON content,
and uploads structured data to various APIs for further processing.
"""

from typing import Dict, List

from pecha_uploader.category import PechaCategory
from pecha_uploader.config import Destination_url, get_logger
from pecha_uploader.index import PechaIndex
from pecha_uploader.link import PechaLink
from pecha_uploader.links.create_ref_json import create_links
from pecha_uploader.term import PechaTerm
from pecha_uploader.text import PechaText
from pecha_uploader.utils import generate_chapters, generate_schema, parse_annotation

logger = get_logger(__name__)


def get_book_title(text: Dict):
    """
    If text source has content, return source book title
    else return target book title
    """
    src_book_title = text["source"]["books"][0]["title"]
    tgt_book_title = text["target"]["books"][0]["title"]

    src_book_content = text["source"]["books"][0]["content"]
    if src_book_content:
        return src_book_title

    return tgt_book_title


def upload(text: Dict, destination_url: Destination_url):
    """
    Read a text file and add.
    """
    payload = {
        "bookKey": "",
        "categoryEn": [],
        "categoryHe": [],
        "textEn": [],
        "textHe": [],
        "bookDepth": 0,
    }
    for lang in text:
        if lang == "source":
            for i in range(len(text[lang]["categories"])):
                payload["categoryEn"].append(text[lang]["categories"][: i + 1])
            for book in text[lang]["books"]:
                payload["bookKey"] = payload["categoryEn"][-1][-1]["name"]
                payload["textEn"].append(book)
        elif lang == "target":
            for i in range(len(text[lang]["categories"])):
                payload["categoryHe"].append(text[lang]["categories"][: i + 1])
            for book in text[lang]["books"]:
                payload["textHe"].append(book)

    try:
        # print("===========================( post_term )===========================")
        category_path = list(map(lambda x: x["name"], payload["categoryEn"][i]))
        for i in range(len(payload["categoryEn"])):
            PechaTerm().post_term(
                payload["categoryEn"][i][-1]["name"],
                payload["categoryHe"][i][-1]["name"],
                destination_url,
            )
            # print("===========================( post_category )===========================")
            PechaCategory().post_category(
                payload["categoryEn"][i], payload["categoryHe"][i], destination_url
            )

        # print(
        #     "============================( post_index )================================"
        # )
        schema = generate_schema(payload["textEn"][0], payload["textHe"][0])

        PechaIndex().post_index(
            payload["bookKey"], payload["categoryEn"][-1], schema[0], destination_url
        )

        # print(
        #     "===============================( post_text )=================================="
        # )
        text_index_key = payload["bookKey"]

        for book in payload["textEn"]:
            process_text(book, "en", text_index_key, category_path, destination_url)

        for book in payload["textHe"]:
            process_text(book, "he", text_index_key, category_path, destination_url)

        if is_commentary(text):
            links_data = create_links(text)
            add_links(links_data, destination_url)

    except Exception as e:
        logger.error(f"{e}")
        raise Exception(f"{e}")


def process_text(
    book: dict,
    lang: str,
    text_index_key: str,
    category_path: List,
    destination_url: Destination_url,
):
    """
    Process text for a given language and post it.
    """
    text = {
        "versionTitle": book["title"],
        "versionSource": book["versionSource"],
        "language": lang,
        "actualLanguage": book["language"],
        "completestatus": book["completestatus"],
        "versionLongNotes": "",
        "versionNotesInTibetan": "",
        "versionNotes": "",
        "text": [],
    }

    if "content" in book:
        # Complex text
        if isinstance(book["content"], dict):
            result = generate_chapters(book["content"], book["language"])

            for key, value in result.items():
                text["text"] = value
                PechaText().post_text(
                    key, text, category_path, destination_url, text_index_key
                )

        # Simple text
        elif isinstance(book["content"], list):
            text["text"] = parse_annotation(book["content"])
            PechaText().post_text(
                text_index_key, text, category_path, destination_url, text_index_key
            )


def add_links(links: List[Dict], destination_url: Destination_url):
    """
    Post root and commentary links
    """
    # remove is links is available
    PechaLink().remove_links(links[0]["refs"][1], destination_url)

    batch_size = 150
    for i in range(0, len(links), batch_size):
        batch = links[i : i + batch_size]  # noqa
        PechaLink().post_link(batch, destination_url)


def is_commentary(text: Dict):
    """
    Return
        True, if text is a Commentary
        False, if text is a Root
    """
    src_last_category = text["source"]["categories"][-1]
    tgt_last_category = text["target"]["categories"][-1]

    if (
        "base_text_titles" in src_last_category
        or "base_text_titles" in tgt_last_category
    ):
        return True

    else:
        return False
