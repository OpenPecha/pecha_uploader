import json
import re
from pathlib import Path
from typing import Dict, List, Any

# Constants
INPUT_FILE_PATH = Path("./data/chapterized_critical_content.json")
OUTPUT_FILE_PATH = "chojuk_processed_output.json"


def remove_superscript(text: str) -> str:
    """Remove superscript text and standardize Tibetan punctuation.
    
    Args:
        text: The input text to process
        
    Returns:
        Processed text with superscripts removed and standardized punctuation
    """
    # Remove superscript numbers using Unicode ranges
    text = re.sub(
        r"[\u00B2\u00B3\u00B9\u2070-\u207F\u1D2C-\u1D6A\u1D9B-\u1DBF]", "", text
    )

    # Standardize Tibetan punctuation
    if "༄༅༅། །" in text:
        text = text.replace("༄༅༅། །", "༄༅༅།།")
    if "༄། །" in text:
        text = text.replace("༄། །", "༄།།")

    # Handle numbered markers after punctuation
    if "། །" in text:
        # If [number] is after "། །" or "ག །", move it before
        pattern = re.compile(r"(། །|ག །)(\s*\[\d+\])")
        text = pattern.sub(lambda match: f"{match.group(2)}{match.group(1)}", text)
        
        # Replace remaining "། །" (not followed by [number])
        text = text.replace("། །", "།།<br>")

    # Replace "ག །" with "ག།<br>"
    if "ག །" in text:
        text = text.replace("ག །", "ག།<br>")

    # Remove trailing <br> if present
    if text.endswith("<br>"):
        text = text[:-4]

    # Fix specific punctuation case
    if "ག།།" in text:
        text = text.replace("ག།།", "ག།")

    return text


def replace_markers(text: str, apparatus: Dict[str, str]) -> str:
    """Replace numbered markers with HTML footnote tags.
    
    Args:
        text: The input text containing markers like [1], [2], etc.
        apparatus: Dictionary mapping marker numbers to their content
        
    Returns:
        Text with markers replaced by HTML footnote tags
    """
    # First remove superscripts
    text = remove_superscript(text)
    
    # Find all markers like [1], [2], etc.
    markers = re.findall(r"\[(\d+)\]", text)
    
    # Replace each marker with HTML tags if it exists in apparatus
    for marker in markers:
        if marker in apparatus:
            replacement = f"<sup class='footnote-marker'>*</sup><i class='footnote'>{apparatus[marker]}</i>"
            text = text.replace(f"[{marker}]", replacement)
            
    return text


def process_json_data(input_data: Dict[str, List[Dict[str, Any]]]) -> List[List[str]]:
    """Process the input JSON data to create the output format.
    
    Args:
        input_data: The loaded JSON data to process
        
    Returns:
        Processed data in the required output format
    """
    output_data = []
    
    for key, value in input_data.items():
        processed_list = []
        for item in value:
            if item["critical_apparatus"]:
                # Replace markers in the text with HTML footnotes
                processed_text = replace_markers(
                    item["critical_edition_with_marker"], 
                    item["critical_apparatus"]
                )
                processed_list.append(processed_text)
            else:
                # Just remove superscripts if no critical apparatus
                processed_list.append(
                    remove_superscript(item["critical_edition_with_marker"])
                )
        output_data.append(processed_list)
    
    return output_data


def main():
    """Main function to process the input file and save the output."""
    try:
        # Load input data
        with INPUT_FILE_PATH.open("r", encoding="utf-8") as f:
            input_json = json.load(f)
        
        # Process the data
        output_json = process_json_data(input_json)
        
        # Print the length of each item for verification
        for item in output_json:
            print(len(item))
        
        # Save the processed output
        with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(output_json, f, ensure_ascii=False, indent=4)
        
        print(f"Processed output saved to {OUTPUT_FILE_PATH}")
        
    except Exception as e:
        print(f"Error processing file: {e}")


if __name__ == "__main__":
    main()