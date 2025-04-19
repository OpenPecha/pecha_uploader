import re
from typing import Dict, List, Union


def generate_schema(enbook: Dict, bobook: Dict, en_key: str = "", bo_key: str = ""):

    nodes = []
    # generate schema node for complex text
    if "content" in bobook:
        botext = bobook["content"]
        entext = enbook["content"]
    else:
        botext = bobook
        entext = enbook

    if isinstance(entext, dict):
        for (enkey, envalue), (bokey, bovalue) in zip(entext.items(), botext.items()):
            en_full_key = enkey.strip() if en_key else enkey
            bo_full_key = bokey.strip() if bo_key else bokey
            if isinstance(envalue, dict) and enkey != "data":
                # Check if the dictionary has any children other than 'data'

                has_children = any(sub_key != "data" for sub_key in envalue.keys())
                child_nodes = generate_schema(
                    envalue, bovalue, en_full_key, bo_full_key
                )
                # if data is only
                if not has_children:
                    data_node = create_data_node(
                        en_full_key, bo_full_key, envalue["data"], bovalue["data"]
                    )
                    nodes.append(data_node)
                else:
                    node = {
                        "nodes": child_nodes,
                        "titles": [
                            {"lang": "he", "text": bo_full_key, "primary": True},
                            {"lang": "en", "text": en_full_key, "primary": True},
                        ],
                        "key": en_full_key,
                    }
                    nodes.append(node)

            elif enkey == "data":
                data_node = create_data_node(enkey, "གནས་བབས", envalue, bovalue)
                nodes.append(data_node)
    if isinstance(entext, list):
        data_node = create_data_node(enbook["title"], bobook["title"], entext, botext)
        nodes.append(data_node)
    return nodes


def create_data_node(
    en_key: str,
    bo_key: str,
    envalue: Union[List[str], List[List]],
    bovalue: Union[List[str], List[List]],
):
    """This function generate node for schema"""
    text_depth = None
    sections = ["Chapters", "Verses", "Paragraphs"]

    if len(envalue) > 0:
        text_depth = get_list_depth(envalue)

    elif len(bovalue) > 0:
        text_depth = get_list_depth(bovalue)

    else:
        text_depth = 1

    return {
        "nodeType": "JaggedArrayNode",
        "depth": text_depth,
        "addressTypes": list(map(lambda x: "Integer", sections[:text_depth])),
        "sectionNames": sections[:text_depth],
        "titles": [
            {"lang": "he", "text": bo_key, "primary": True},
            {"lang": "en", "text": en_key, "primary": True},
        ],
        "key": en_key,
    }


def parse_annotation(value: Union[List[str], List[List]]):
    """clean and parse annotation"""

    def process_item(item):
        # If the item is a list, recursively process its contents
        if isinstance(item, list):
            return [process_item(sub_item) for sub_item in item]

        # Convert item to string and apply transformations
        if not isinstance(item, str):
            item = str(item)

        # Replace newlines
        item = item.replace("\n", "<br>")

        # Sapche transformation
        if "<sapche>" in item:
            item = item.replace("<sapche>", '<span class="text-subche-style">')
            item = item.replace("</sapche>", "</span>")

        # Citation transformation
        if "{" in item:
            item = item.replace("{", '<span class="text-citation-style">')
            item = item.replace("}", "</span>")

        # Quotation transformation
        if "(" in item:
            item = item.replace("(", '<span class="text-quotation-style">')
            item = item.replace(")", "</span>")

        # Remove numbered tags
        item = re.sub(r"<\d+>", "", item.strip())

        return item

    # Process the entire input recursively
    return process_item(value)


def generate_chapters(
    book: List[Dict],
    language: str,
    current_key: str = "",
    parent_keys: List[str] = None,
):
    """generate text content"""
    result = {}
    if parent_keys is None:
        parent_keys = []

    for key, value in book.items():
        full_key = key if current_key else key
        new_parent_keys = parent_keys + [key.strip()]  # Update list of parent key
        clean_value = []
        if isinstance(value, dict):

            # Check if the dictionary has any children other than 'data'
            has_children = any(sub_key != "data" for sub_key in value.keys())
            child_data = generate_chapters(value, language, full_key, new_parent_keys)
            result.update(child_data)  # Merge results from children

            # Determine the key for 'data' depending on whether there are other children
            if "data" in value:
                clean_value = parse_annotation(value["data"])

                # If there are other children, include 'data' in the key, else exclude it
            if has_children:
                if language == "bo":
                    data_key = ", ".join(new_parent_keys) + ", གནས་བབས"
                else:
                    data_key = ", ".join(new_parent_keys) + ", data"
            else:
                data_key = ", ".join(
                    new_parent_keys
                )  # Exclude 'data' from the key if no other children
            result[data_key] = clean_value

    return result


def get_list_depth(lst):
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
