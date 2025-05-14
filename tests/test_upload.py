import json
from pecha_uploader.pipeline import upload

def read_json(json_path):
    with open(json_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    base_pecha_json = read_json("./tests/data/base_text.json")
    commentary_pecha_json = read_json("./tests/data/commentary_text.json")
    destination_url = "https://staging.pecha.org/"
    upload(base_pecha_json, destination_url)
    upload(commentary_pecha_json, destination_url)