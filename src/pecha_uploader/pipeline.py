"""
This module processes text files, parses JSON content,
and uploads structured data to various APIs for further processing.
"""
import json
import os

from pecha_uploader.category.upload import post_category
from pecha_uploader.config import BASEPATH
from pecha_uploader.index.upload import post_index
from pecha_uploader.links.create_ref_json import commentaryToRoot
from pecha_uploader.links.upload import post_link
from pecha_uploader.preprocess.upload import post_term
from pecha_uploader.text.upload import post_text
from pecha_uploader.utils import generate_chapters, generate_schema, parse_annotation


def add_texts(text_type):
    """
    Add all text files in `/jsondata/texts`.
    """
    text_list = os.listdir(f"{BASEPATH}/jsondata/texts/{text_type}")
    try:  # Added text save to `success.txt`
        with open(f"{BASEPATH}/jsondata/texts/success.txt", encoding="utf-8") as f:
            uploaded_text_list = f.read().split("\n")
    except Exception as e:
        print("read text error :", e)
        uploaded_text_list = []

    count = 0
    for data in text_list:
        count += 1
        print(f"{count}/{len(text_list)}")
        if data in uploaded_text_list:
            continue
        elif data == "success.txt":
            continue
        text_upload_succeed = add_by_file(data, text_type)

        if not text_upload_succeed:
            print("=== [Failed] ===")
            return
        print(f"=== [Finished] {data} ===")


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
            print("\nterm : ", response)
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
            print("categories: ", category_response)
            if not category_response["status"]:
                error = category_response["error"]
                log_error("Category", text_name, f"{error}")
                return False

        print(
            "============================( post_index )================================"
        )
        schema = generate_schema(payload["textEn"][0], payload["textHe"][0])

        # serialized_schema = serialize_schema(schema)
        # j = json.dumps(schema, indent=4, ensure_ascii=False)
        # print(j)
        index_response = post_index(
            payload["bookKey"], payload["categoryEn"][-1], schema[0]
        )
        print("index : ", index_response)
        if not index_response["status"]:
            error = index_response["error"]
            log_error("Index", text_name, f"{error}")
            return False

        print(
            "===============================( post_text )=================================="
        )
        text_index_key = payload["bookKey"]

        for book in payload["textEn"]:
            if not process_text(book, "en", text_index_key):
                return False

        for book in payload["textHe"]:
            if not process_text(book, "he", text_index_key):
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
            # j = json.dumps(result, indent=4, ensure_ascii=False
            # print(j)
            is_succeed = False
            errors = []
            for key, value in result.items():
                text["text"] = value
                text_response = post_text(key, text)
                print("response", text_response)
                if not text_response["status"]:
                    error = text_response["error"]
                    errors.append(error)
                    log_error("Text", key, f"{error}")
                    is_succeed = False
                else:
                    is_succeed = True

            if is_succeed:
                log_error("Text", text_index_key, f"{errors}")

            return is_succeed

        # Simple text
        elif isinstance(book["content"], list):
            text["text"] = parse_annotation(book["content"])
            text_response = post_text(text_index_key, text)
            print("response", text_response)
            if not text_response["status"]:
                error = text_response["error"]
                log_error("Text", text_index_key, f"{error}")
                return False
            else:
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
        f"{BASEPATH}/jsondata/texts/errors.txt", mode="a", encoding="utf-8"
    ) as error_file:  # noqa
        error_file.write(f"({api_name})--->{text_name}: {message}\n\n")


def add_refs():
    """
    Add all ref files in `/jsondata/links`.
    """
    print("============ add_refs ============")
    file_list = os.listdir(f"{BASEPATH}/jsondata/links")
    try:  # Added refs save to `success.txt`
        with open(f"{BASEPATH}/jsondata/links/success.txt", encoding="utf-8") as f:
            ref_success_list = f.read().split("\n")
    except Exception as e:
        print("Ref error : ", e)
        ref_success_list = []
    failed_list = []
    print(ref_success_list)
    for file in file_list:
        if file in ref_success_list:
            continue
        elif file == "success.txt":
            continue
        elif file == "errors.txt":
            continue

        with open(f"{BASEPATH}/jsondata/links/{file}", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                raise ValueError("File is empty")
            try:
                ref_list = json.loads(content)
            except Exception as e:
                raise ValueError(f"Invalid JSON: {e}")
            # remove_links(ref_list[0]["refs"][1])
        for ref in ref_list:
            # Separate refs since the API only support adding 2 refs at the same time.
            for i in range(0, len(ref["refs"]) - 1):
                for j in range(i + 1, len(ref["refs"])):
                    link_response = post_link(
                        [ref["refs"][i], ref["refs"][j]], ref["type"]
                    )

                    # Failed
                    if not link_response["status"]:
                        failed_list.append(link_response["res"])
        with open(
            f"{BASEPATH}/jsondata/links/success.txt", mode="a", encoding="utf-8"
        ) as f:
            f.write(file + "\n")
        print(f"=== [Finished] {file} ===")
    with open(
        f"{BASEPATH}/jsondata/links/errors.txt", mode="w+", encoding="utf-8"
    ) as f:
        json.dump(failed_list, f, indent=4, ensure_ascii=False)


# ----------------Main------------------


def main():
    """
    Add all files in `/jsondata`
    """
    print("============================= texts =================================")
    if not os.path.exists(f"{BASEPATH}/jsondata/texts"):
        os.mkdir(f"{BASEPATH}/jsondata/texts/baseText")
        os.mkdir(f"{BASEPATH}/jsondata/texts/commentaryText")

    commentaryToRoot("commentaryText")
    add_texts("baseText")
    add_texts("commentaryText")

    print("============================== refs ==================================")
    if not os.path.exists(f"{BASEPATH}/jsondata/links"):
        os.mkdir(f"{BASEPATH}/jsondata/links")
    add_refs()


if __name__ == "__main__":
    main()
