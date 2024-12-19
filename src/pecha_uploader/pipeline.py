"""
This module processes text files, parses JSON content,
and uploads structured data to various APIs for further processing.
"""
import json

from pecha_uploader.category.upload import post_category
from pecha_uploader.config import BASEPATH
from pecha_uploader.index.upload import post_index
from pecha_uploader.preprocess.upload import post_term
from pecha_uploader.text.upload import post_text
from pecha_uploader.utils import generate_chapters, generate_schema, parse_annotation


def add_by_file(text_name: str, text_type: str):
    """
    Read a text file and add.
    """
    file = f"{BASEPATH}/jsondata/texts/{text_type}/{text_name}"

    print(f"=========================={text_name}===========================")

    try:
        with open(file, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_error("file", text_name, f"Error opening file: {e}")
        return False

    payload = {
        "bookKey": "",
        "categoryEn": [],
        "categoryHe": [],
        "textEn": [],
        "textHe": [],
        "bookDepth": 0,
    }

    try:
        for lang in data:
            if lang == "source":
                for i in range(len(data[lang]["categories"])):
                    payload["categoryEn"].append(data[lang]["categories"][: i + 1])
                for book in data[lang]["books"]:
                    payload["bookKey"] = payload["categoryEn"][-1][-1]["name"]
                    payload["textEn"].append(book)
            elif lang == "target":
                for i in range(len(data[lang]["categories"])):
                    payload["categoryHe"].append(data[lang]["categories"][: i + 1])
                for book in data[lang]["books"]:
                    payload["textHe"].append(book)
    except Exception as e:
        log_error("Payload", text_name, f"Error parsing data: {e}")
        return False

    try:
        print("===========================( post_category )===========================")
        for i in range(len(payload["categoryEn"])):
            response = post_term(
                payload["categoryEn"][i][-1]["name"],
                payload["categoryHe"][i][-1]["name"],
            )
            if not response["status"]:
                if "term_conflict" in response:
                    error = response["term_conflict"]
                    log_error("Term", text_name, f"{error}")
                else:
                    log_error("Term", text_name, f"{response}")
                return False

            category_response = post_category(
                payload["categoryEn"][i], payload["categoryHe"][i]
            )
            if not category_response["status"]:
                error = category_response["error"]
                log_error("Category", text_name, f"{error}")
                return False

        print(
            "============================( post_index )================================"
        )
        schema = generate_schema(payload["textEn"][0], payload["textHe"][0])
        index_response = post_index(
            payload["bookKey"], payload["categoryEn"][-1], schema[0]
        )
        if not index_response["status"]:
            error = index_response["error"]
            log_error("Index", text_name, f"{error}")
            return False

        print(
            "=============================( post_text )================================="
        )
        text_index_key = payload["bookKey"]

        for book in payload["textHe"]:
            if not process_text(book, "he", text_index_key):
                return False

        for book in payload["textEn"]:
            if not process_text(book, "en", text_index_key):
                return False

    except Exception as e:
        print("Error : ", e)
        return False

    with open(
        f"{BASEPATH}/jsondata/texts/success.txt", mode="a", encoding="utf-8"
    ) as f:
        f.write(f"{text_name}\n")

    return True


def process_text(book: dict, lang: str, text_index_key: str):
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
            for key, value in result.items():
                text["text"] = value
                text_response = post_text(key, text)
                if value and not text_response["status"]:
                    error = text_response["error"]
                    log_error("Text", key, f"{error}")
                    return False

        # Simple text
        elif isinstance(book["content"], list):
            text["text"] = parse_annotation(book["content"])
            text_response = post_text(key, text)
            if not text_response["status"]:
                error = text_response["error"]
                log_error("Text", text_index_key, f"{error}")
                return False

    return True


def log_error(api_name: str, text_name: str, message: str):
    """
    Logs error details to a designated error file.

    Args:
        api_name (str): The name of the API where the error occurred.
        text_name (str): The name of the text file being processed.
        message (str): A descriptive error message.

    Writes:
        The error details into an `errors.txt` file located at
        `{BASEPATH}/pecha_uploader/texts/`.
    """
    with open(
        f"{BASEPATH}/pecha_uploader/texts/errors.txt", mode="a", encoding="utf-8"
    ) as error_file:  # noqa
        error_file.write(f"({api_name})--->{text_name}: {message}\n\n")
