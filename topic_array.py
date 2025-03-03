import json
from pathlib import Path

text_path = Path("chojuk_processed_output.json")

with text_path.open("r", encoding="utf-8") as f:
    log_entries = json.load(f)
    print(log_entries)

    # List to store the extracted topics
    topics = []

    # Iterate through each log entry
    for entry in log_entries:
        # Parse the JSON-like string
        # Extract the event message
        event_message = entry["event"]
        # Extract the topic slug from the event message
        if "non-existant topic slug:" in event_message:
            topic = event_message.split("non-existant topic slug:")[1].strip()
            topics.append(topic)

    # Print the list of topics
    print(topics)

output_file = "topic_output.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(topics, f, ensure_ascii=False, indent=4)
