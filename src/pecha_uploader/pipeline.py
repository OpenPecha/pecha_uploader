"""
This module processes text files, parses JSON content,
and uploads structured data to various APIs for further processing.
"""

import os
from typing import Dict, List

from pecha_uploader.category.upload import post_category
from pecha_uploader.config import (
    LINK_JSON_PATH,
    TEXT_SUCCESS_LOG,
    Destination_url,
    log_link_success,
    logger,
)
from pecha_uploader.index.upload import post_index
from pecha_uploader.links.create_ref_json import commentaryToRoot
from pecha_uploader.links.delete import remove_links
from pecha_uploader.links.upload import post_link
from pecha_uploader.preprocess.upload import post_term
from pecha_uploader.text.upload import post_text
from pecha_uploader.utils import (
    generate_chapters,
    generate_schema,
    parse_annotation,
    read_json,
)


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


def add_texts(text: Dict, overwrite: bool, destination_url: Destination_url):

    if overwrite:
        uploaded_text_list = []
    else:
        uploaded_text_list = (
            TEXT_SUCCESS_LOG.read_text(encoding="utf-8").splitlines()
            if TEXT_SUCCESS_LOG.exists()
            else []
        )

    book_title = get_book_title(text)

    if book_title not in uploaded_text_list:
        add_by_file(text, destination_url)

        # if not text_upload_succeed:
        #     log_error(TEXT_ERROR_LOG, f"{book_title}[json file]", "file not uploaded")


def add_by_file(text: Dict, destination_url: Destination_url):
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
            post_term(
                payload["categoryEn"][i][-1]["name"],
                payload["categoryHe"][i][-1]["name"],
                destination_url,
            )
            # print("===========================( post_category )===========================")
            post_category(
                payload["categoryEn"][i], payload["categoryHe"][i], destination_url
            )

        # print(
        #     "============================( post_index )================================"
        # )
        schema = generate_schema(payload["textEn"][0], payload["textHe"][0])

        post_index(
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
                post_text(key, text, category_path, destination_url, text_index_key)

        # Simple text
        elif isinstance(book["content"], list):
            text["text"] = parse_annotation(book["content"])
            post_text(
                text_index_key, text, category_path, destination_url, text_index_key
            )


def add_refs(destination_url: Destination_url):
    """
    Add all ref files in `/jsondata/links`.
    """
    # print("============ add_refs ============")
    file_list = LINK_JSON_PATH.glob("*.json")
    # ref_success_list = (
    #     LINK_SUCCESS_LOG.read_text(encoding="utf-8").splitlines()
    #     if LINK_SUCCESS_LOG.exists()
    #     else []
    # )

    for file_path in file_list:
        file_name = os.path.basename(file_path)
        # if file_name in ref_success_list:
        #     continue
        ref_list = read_json(file_path)

        remove_links(ref_list[0]["refs"][1], destination_url)

        batch_size = 150
        for i in range(0, len(ref_list), batch_size):
            batch = ref_list[i : i + batch_size]  # noqa
            post_link(batch, destination_url)

        # # store link success
        log_link_success(os.path.basename(file_name))


def upload_root(
    text: Dict,
    destination_url: Destination_url,
    overwrite: bool = False,
):
    """
    Upload root text to the API.
    """
    add_texts(text, overwrite, destination_url)


def upload_commentary(
    text: Dict,
    destination_url: Destination_url,
    overwrite: bool = False,
):

    """
    Upload commentary text to the API.
    """

    # create link json
    commentaryToRoot(text)
    # upload commentary json
    add_texts(text, overwrite, destination_url)

    # upload link json for commentary
    add_refs(destination_url)


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


def upload(text: Dict, destination_url: Destination_url, overwrite: bool = False):
    if is_commentary(text):
        upload_commentary(text, destination_url, overwrite)
    else:
        upload_root(text, destination_url, overwrite)
