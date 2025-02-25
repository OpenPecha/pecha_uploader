import json
import re
from pathlib import Path

text_path = Path("chapterized_critical_content.json")

# Function to replace markers with HTML tags


def replace_markers(text, apparatus):
    # Use regex to find all markers like [1], [2], etc.
    markers = re.findall(r"\[(\d+)\]", text)
    for marker in markers:
        if marker in apparatus:
            # Replace the marker with the HTML tags
            replacement = (
                f"<sup>{marker}</sup> <i class='footnote'>{apparatus[marker]}</i>"
            )
            text = text.replace(f"[{marker}]", replacement)
    return text


# Process each item in the JSON data
with text_path.open("r", encoding="utf-8") as f:
    input_json = json.load(f)
    output_json = []
    for key, value in input_json.items():
        processed_list = []
        for item in value:
            if item["critical_apparatus"]:
                # Replace markers in the critical_edition_with_marker field
                processed_text = replace_markers(
                    item["critical_edition_with_marker"], item["critical_apparatus"]
                )
                processed_list.append(processed_text)
            else:
                processed_list.append(item["critical_edition_with_marker"])
        output_json.append(processed_list)

# Save the result to a JSON file
output_file = "chojuk_processed_output.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_json, f, ensure_ascii=False, indent=4)

print(f"Processed output saved to {output_file}")
