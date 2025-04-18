from pecha_uploader.category import PechaCategory
from pecha_uploader.config import Destination_url
from pecha_uploader.index.delete import remove_index
from pecha_uploader.preprocess.delete import remove_term


def remove_texts_meta(meta_list: dict, destination_url: Destination_url):

    if "term" in meta_list and "category" not in meta_list:
        remove_term(meta_list["term"], destination_url)
    if "index" in meta_list:
        remove_index(meta_list["index"], destination_url)
    if "category" in meta_list:
        for cat in transform_category_list(meta_list["category"]):
            res_cat = PechaCategory().remove_category(cat, destination_url)

            # if category doesn't exist, remove term
            if "error" in res_cat and "doesn't exist" in res_cat:
                remove_term(cat[-1], destination_url)
            # if category is removed, remove term
            elif "status" in res_cat:
                remove_term(cat[-1], destination_url)


def transform_category_list(categories):
    """
    Transform a flat list of categories into nested sublists in reverse order.
    Example: ["a", "b", "c"] -> [["a", "b", "c"], ["a", "b"], ["a"]]
    """
    return [categories[: i + 1] for i in range(len(categories) - 1, -1, -1)]
