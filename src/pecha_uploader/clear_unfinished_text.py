from pecha_uploader.category.delete import remove_category
from pecha_uploader.config import Destination_url
from pecha_uploader.index.delete import remove_index
from pecha_uploader.preprocess.delete import remove_term


def remove_texts_meta(meta_list: dict, destination_url: Destination_url):

    if "term" in meta_list:
        remove_term(meta_list["term"], destination_url)
    if "category" in meta_list:
        remove_category(meta_list["category"], destination_url)
    if "index" in meta_list:
        remove_index(meta_list["index"], destination_url)
