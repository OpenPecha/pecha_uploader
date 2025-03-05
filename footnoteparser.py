import json
import re
from pathlib import Path

text_path = Path("chapterized_critical_content.json")


# Function to remove superscript text (e.g., ¹, ², ³, ⁴)
def remove_superscript(text):
    # Use regex to remove superscript numbers
    text = re.sub(
        r"[\u00B2\u00B3\u00B9\u2070-\u207F\u1D2C-\u1D6A\u1D9B-\u1DBF]", "", text
    )

    # If the text ends with "། །", replace it with "།།" (without <br>)

    # Replace "༄༅༅། །" with "༄༅༅།།"
    if "༄༅༅། །" in text:
        text = text.replace("༄༅༅། །", "༄༅༅།།")
    if "༄། །" in text:
        text = text.replace("༄། །", "༄།།")

    # Replace "། །" with "།།<br>", but not if it's at the end of the string
    if "། །" in text:
        # If [number] is after "། །" or "ག །", move it before
        pattern = re.compile(r"(། །|ག །)(\s*\[\d+\])")

        def reorder(match):
            return f"{match.group(2)}{match.group(1)}"

        text = pattern.sub(reorder, text)
        # Replace remaining "། །" (not followed by [number])
        text = text.replace("། །", "།།<br>")

    # Replace "ག །" with "ག།<br>"
    if "ག །" in text:
        text = text.replace("ག །", "ག།<br>")
    # Remove the last <br> if it exists

    if text.endswith("<br>"):
        text = text[:-4]

    if "ག།།" in text:
        text = text.replace("ག།།", "ག།")

    return text


# Function to replace markers with HTML tags
def replace_markers(text, apparatus):
    # Use regex to find all markers like [1], [2], etc.
    markers = re.findall(r"\[(\d+)\]", text)
    text = remove_superscript(text)
    for marker in markers:
        if marker in apparatus:
            # Replace the marker with the HTML tags
            replacement = f"<sup class='footnote-marker'>*</sup><i class='footnote'>{apparatus[marker]}</i>"
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
                processed_list.append(
                    remove_superscript(item["critical_edition_with_marker"])
                )
        output_json.append(processed_list)
for item in output_json:
    print(len(item))
# Save the result to a JSON file
output_file = "chojuk_processed_output.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_json, f, ensure_ascii=False, indent=4)

print(f"Processed output saved to {output_file}")
