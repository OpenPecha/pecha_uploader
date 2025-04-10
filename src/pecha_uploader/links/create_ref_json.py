import re
from typing import Any, Dict, List


def link_mapper(title: str, contents: List, root_detail: Dict):
    """'buld refs json file"""
    links = []
    refs = {}
    root_title = root_detail["base_text_titles"][0]
    if get_list_depth(contents) == 1:
        # for dept 1
        constent_range = get_range(contents)
        for value in constent_range:
            tag = value[1]
            ref = []
            ref.append(f"{root_title} {tag[1][0]}:{tag[1][1]}")  # noqa
            ref.append(f"{title} {tag[0]}")
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
                    for value in constent_range:

                        tag = value[1]
                        ref = []
                        ref.append(f"{root_title} {tag[1][0]}:{tag[1][1]}")  # noqa
                        ref.append(f"{title} {i+1}:{tag[0]}")  # noqa
                        refs["refs"] = ref
                        refs["type"] = "commentary"
                        links.append(refs)
                        refs = {}
                else:
                    for j, data in enumerate(content):
                        if isinstance(data, list):
                            # for dept 3
                            constent_range = get_range(data)
                            for value in constent_range:
                                tag = value[1]
                                ref = []
                                ref.append(
                                    f"{root_title} {tag[1][0]}:{tag[1][1]}"  # noqa
                                )
                                ref.append(f"{title} {i+1}:{j+1}:{tag[0]}")  # noqa
                                refs["refs"] = ref
                                refs["type"] = "commentary"
                                links.append(refs)
                                refs = {}
    return links


def get_range(data: List[str]):
    """Return list of (tag, [range, nums]) with duplicates allowed."""
    tag_to_lines = {}

    # Collect line numbers for each tag
    for i, line in enumerate(data):
        line_num = i + 1
        tags = re.findall(r"<\d+,\d+>", line)
        for tag in tags:
            tag_to_lines.setdefault(tag, []).append(line_num)

    result = []

    # Sort tags by numeric value
    for tag in sorted(
        tag_to_lines.keys(), key=lambda x: list(map(int, re.findall(r"\d+", x)))
    ):
        nums = list(map(int, re.findall(r"\d+", tag)))
        lines = tag_to_lines[tag]

        # Split into contiguous groups
        group = [lines[0]]
        for curr, next_one in zip(lines, lines[1:] + [None]):
            if next_one is None or next_one != curr + 1:
                if len(group) == 1:
                    result.append((tag, [str(group[0]), nums]))
                else:
                    result.append((tag, [f"{group[0]}-{group[-1]}", nums]))
                if next_one:
                    group = [next_one]
            else:
                group.append(next_one)
    return result


def create_links(json_text: Dict):
    """map link for echa language"""
    book_last_category = json_text["source"]["categories"][-1]
    index_key = book_last_category["name"]

    # English version
    for enbook in json_text["source"]["books"]:
        chapters = generate_chapters({}, enbook, enbook["language"], index_key)
        for key, value in chapters.items():
            links = link_mapper(key, value, book_last_category)

    # Tibetan version
    for bobook in json_text["target"]["books"]:
        chapters = generate_chapters(
            bobook, json_text["source"]["books"][0], bobook["language"], index_key
        )
        for key, value in chapters.items():
            links = link_mapper(key, value, book_last_category)

    return links


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
