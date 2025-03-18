import json
import re
from collections import defaultdict
from typing import Any, Dict, List

from pecha_uploader.config import LINK_JSON_PATH


def commentaryToRoot(text: Dict):
    """
    Create link for commentary json file based on its mapped root json file.
    """
    create_links(text)


def link_mapper(title: str, contents: List, root_detail: Dict):
    """'buld refs json file"""
    links = []
    refs = {}
    root_title = root_detail["base_text_titles"][0]
    if get_list_depth(contents) == 1:
        # for dept 1
        constent_range = get_range(contents)
        for value in constent_range.values():
            ref = []
            ref.append(f"{root_title} {value[1][0]}:{value[1][1]}")  # noqa
            ref.append(f"{title} {value[0]}")
            refs["refs"] = ref
            refs["type"] = "commentary"
            links.append(refs)
            refs = {}
    else:
        for i, content in enumerate(contents):
            if isinstance(content, list):
                if get_list_depth(content) == 1:
                    # for dept 2
                    constent_range = get_range(content)
                    for value in constent_range.values():
                        ref = []
                        ref.append(f"{root_title} {value[1][0]}:{value[1][1]}")  # noqa
                        ref.append(f"{title} {i+1}:{value[0]}")  # noqa
                        refs["refs"] = ref
                        refs["type"] = "commentary"
                        links.append(refs)
                        refs = {}
                else:
                    for j, data in enumerate(content):
                        if isinstance(data, list):
                            # for dept 3
                            constent_range = get_range(data)
                            for value in constent_range.values():
                                ref = []
                                ref.append(
                                    f"{root_title} {value[1][0]}:{value[1][1]}"  # noqa
                                )
                                ref.append(f"{title} {i+1}:{j+1}:{value[0]}")  # noqa
                                refs["refs"] = ref
                                refs["type"] = "commentary"
                                links.append(refs)
                                refs = {}
    if links:
        commentary_title = title.strip()
        with open(
            LINK_JSON_PATH / f"{commentary_title[-30:]}.json", "w", encoding="utf-8"
        ) as file:
            json.dump(links, file, indent=4, ensure_ascii=False)


def get_range(data: List):
    """build json data"""
    indices = defaultdict(list)

    for i, elem in enumerate(data):
        matches = re.search(r"<\d+><\d+>", elem)
        if matches:
            unique_elem = matches.group()
            indices[unique_elem].append(i)

    output = {}
    for key, value in indices.items():
        output[key] = []
        initial_index = value[0]
        final_index = value[-1]
        if initial_index == final_index:
            output[key].append(str(initial_index + 1))
            match = re.findall(r"\d+", key)
            output[key].append(list(map(int, match)))
        else:
            output[key].append(f"{initial_index + 1}-{final_index + 1}")
            match = re.findall(r"\d+", key)
            output[key].append(list(map(int, match)))

    return output


def create_links(json_data: Dict):
    """map link for echa language"""
    book_last_category = json_data["source"]["categories"][-1]
    index_key = book_last_category["name"]

    # check if json_data is commentary text or not
    if "link" in book_last_category:

        # English version
        for enbook in json_data["source"]["books"]:
            chapters = generate_chapters({}, enbook, enbook["language"], index_key)

            for key, value in chapters.items():
                link_mapper(key, value, book_last_category)

        # Tibetan version
        for bobook in json_data["target"]["books"]:
            chapters = generate_chapters(
                bobook, json_data["source"]["books"][0], bobook["language"], index_key
            )
            for key, value in chapters.items():
                link_mapper(key, value, book_last_category)


def generate_chapters(
    botext: Dict,
    entext: Dict,
    language: str,
    index_key: str,
    current_key: str = "",
    parent_keys: Any = [],
):
    """get chapter from json"""
    result = {}
    enbook = []
    bobook = []
    if "content" in entext:
        enbook = entext["content"]
        if botext:
            bobook = botext["content"]

    else:
        if botext:
            bobook = botext
        enbook = entext

    if isinstance(enbook, dict):
        if not botext:
            for key, value in enbook.items():
                full_key = key if current_key else key
                new_parent_keys = parent_keys + [key.strip()]

                if isinstance(value, dict):
                    # Check if the dictionary has any children other than data
                    has_children = any(sub_key != "data" for sub_key in value.keys())
                    child_data = generate_chapters(
                        value, language, full_key, new_parent_keys
                    )
                    result.update(child_data)  # Merge results from children

                    # If there are other children, include data in the key, else exclude it
                    if has_children:
                        if language == "bo":
                            data_key = (
                                ", ".join(new_parent_keys)
                                + ", གོང་གི་ས་བཅད་ཀྱི་ནང་དོན།"
                            )
                        else:
                            data_key = ", ".join(new_parent_keys) + ", data"
                    else:
                        data_key = ", ".join(
                            new_parent_keys
                        )  # Exclude data from the key if no other children
                    result[data_key] = value["data"]
        else:
            for (enkey, envalue), (bokey, bovalue) in zip(
                enbook.items(), bobook.items()
            ):
                full_key = enkey if current_key else enkey
                new_parent_keys = parent_keys + [enkey.strip()]
                if isinstance(envalue, dict):
                    # Check if the dictionary has any children other than data
                    has_children = any(sub_key != "data" for sub_key in envalue.keys())
                    child_data = generate_chapters(
                        bovalue, envalue, language, full_key, new_parent_keys
                    )
                    result.update(child_data)  # Merge results from children
                    if has_children:
                        data_key = ", ".join(new_parent_keys) + ", data"
                    else:
                        data_key = ", ".join(new_parent_keys)
                    if language == "bo":
                        result[data_key] = bovalue["data"]
                    else:
                        result[data_key] = envalue["data"]

    if isinstance(enbook, list):
        if len(enbook) > 0:
            result[index_key] = enbook
        if len(bobook) > 0:
            result[index_key] = bobook
    return result


def get_list_depth(lst: List):
    """
    Function to calculate the depth of a nested list.
    """
    if not isinstance(lst, list):  # Base case: not a list, no depth
        return 0
    else:
        max_depth = 0
        for item in lst:
            max_depth = max(
                max_depth, get_list_depth(item)
            )  # Recurse and update max depth
        return max_depth + 1  # Add one to include the current depth level
