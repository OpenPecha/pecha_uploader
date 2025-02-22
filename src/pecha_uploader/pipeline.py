"""
This module processes text files, parses JSON content,
and uploads structured data to various APIs for further processing.
"""

from typing import Dict

from pecha_uploader.category.upload import post_category
from pecha_uploader.config import (
    LINK_ERROR_ID_LOG,
    LINK_ERROR_LOG,
    LINK_JSON_PATH,
    LINK_SUCCESS_LOG,
    TEXT_ERROR_ID_LOG,
    TEXT_ERROR_LOG,
    TEXT_SUCCESS_LOG,
    Destination_url,
    log_error,
    log_error_id,
    log_success,
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
        text_upload_succeed = add_by_file(text, destination_url)

        if not text_upload_succeed:
            log_error(TEXT_ERROR_LOG, f"{book_title}[json file]", "file not uploaded")
            log_error_id(TEXT_ERROR_ID_LOG, book_title)


def add_by_file(text: Dict, destination_url: Destination_url):
    """
    Read a text file and add.
    """

    book_title = get_book_title(text)

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
        # print("===========================( post_category )===========================")
        for i in range(len(payload["categoryEn"])):
            response = post_term(
                payload["categoryEn"][i][-1]["name"],
                payload["categoryHe"][i][-1]["name"],
                destination_url,
            )
            if not response["status"]:
                if "term_conflict" in response:
                    log_error(
                        TEXT_ERROR_LOG,
                        f"{book_title}[term]",
                        f"{response['term_conflict']}",
                    )
                    log_error_id(TEXT_ERROR_ID_LOG, book_title.name)
                else:
                    log_error(TEXT_ERROR_LOG, f"{book_title.name}[term]", f"{response}")
                    log_error_id(TEXT_ERROR_ID_LOG, book_title.name)
                return False

            category_response = post_category(
                payload["categoryEn"][i], payload["categoryHe"][i], destination_url
            )
            if not category_response["status"]:
                log_error(
                    TEXT_ERROR_LOG,
                    f"{book_title}[category]",
                    f"{category_response['error']}",
                )
                log_error_id(TEXT_ERROR_ID_LOG, book_title)
                return False

        # print(
        #     "============================( post_index )================================"
        # )
        schema = generate_schema(payload["textEn"][0], payload["textHe"][0])

        index_response = post_index(
            payload["bookKey"], payload["categoryEn"][-1], schema[0], destination_url
        )
        if not index_response["status"]:
            log_error(
                TEXT_ERROR_LOG,
                f"{book_title}[index]",
                f"{index_response['error']}",
            )
            log_error_id(TEXT_ERROR_ID_LOG, book_title)
            return False

        # print(
        #     "===============================( post_text )=================================="
        # )
        text_index_key = payload["bookKey"]

        for book in payload["textEn"]:
            if not process_text(book, "en", text_index_key, destination_url):
                return False

        for book in payload["textHe"]:
            if not process_text(book, "he", text_index_key, destination_url):
                return False

    except Exception as e:
        print("exception : ", e)
        return False

    log_success(TEXT_SUCCESS_LOG, book_title)

    return True


def process_text(
    book: dict, lang: str, text_index_key: str, destination_url: Destination_url
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
        "text": [],
    }

    if "content" in book:
        # Complex text
        if isinstance(book["content"], dict):
            result = generate_chapters(book["content"], book["language"])
            is_succeed = False
            errors = []
            for key, value in result.items():
                text["text"] = value
                text_response = post_text(key, text, destination_url)
                if not text_response["status"]:
                    error = text_response["error"]
                    errors.append(error)
                    is_succeed = False
                else:
                    is_succeed = True

            if is_succeed:
                log_error(TEXT_ERROR_LOG, f"{text_index_key}[text]", f"{errors}")
                log_error_id(TEXT_ERROR_ID_LOG, text_index_key)

            return is_succeed

        # Simple text
        elif isinstance(book["content"], list):
            text["text"] = parse_annotation(book["content"])
            text_response = post_text(text_index_key, text, destination_url)
            if not text_response["status"]:
                error = text_response["error"]
                log_error(
                    TEXT_ERROR_LOG,
                    f"{text_index_key}[text]",
                    f"{text_response['error']}",
                )
                log_error_id(TEXT_ERROR_ID_LOG, text_index_key)
                return False
            else:
                return True


def add_refs(destination_url: Destination_url):
    """
    Add all ref files in `/jsondata/links`.
    """
    # print("============ add_refs ============")
    file_list = LINK_JSON_PATH.glob("*.json")
    ref_success_list = (
        LINK_SUCCESS_LOG.read_text(encoding="utf-8").splitlines()
        if LINK_SUCCESS_LOG.exists()
        else []
    )
    for file in file_list:
        if file in ref_success_list:
            continue

        ref_list = read_json(file)

        remove_links(ref_list[0]["refs"][1], destination_url)

        for ref in ref_list:
            # Separate refs since the API only support adding 2 refs at the same time.
            for i in range(0, len(ref["refs"]) - 1):
                for j in range(i + 1, len(ref["refs"])):
                    link_response = post_link(
                        [ref["refs"][i], ref["refs"][j]], ref["type"], destination_url
                    )
                    # Failed
                    if not link_response["status"]:
                        log_error(LINK_ERROR_LOG, f"{file}[link]", link_response["res"])
                        log_error_id(LINK_ERROR_ID_LOG, file)

        log_success(LINK_SUCCESS_LOG, file)
        # print(f"=== [Finished] {file} ===")


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
