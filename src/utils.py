import os
import json
import base64
import logging
from typing import Any, List
from datetime import datetime
from mimetypes import guess_type


# Custom serializer for JSON serialisation
def custom_serialiser(obj):
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    elif isinstance(obj, list):
        return [custom_serialiser(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: custom_serialiser(value) for key, value in obj.items()}
    else:
        return obj


# Serialise a list of objects to JSON
def serialise(objects: List[Any]) -> str:
    obj_json = json.dumps(objects, default=custom_serialiser, indent=4)
    return obj_json


# Convert a local image to a data URL
def convert_local_image_to_data_url(image_path: str) -> str:
    mime_type, _ = guess_type(image_path)

    if mime_type is None:
        mime_type = "application/octet-stream"

    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{base64_encoded_data}"


# Read contents from file
def read_file(filename: str) -> str:
    # Check if the file exists
    if os.path.exists(filename):
        logging.info(f"Reading file {filename}...")
        try:
            with open(filename, "r") as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error reading file {filename}: {e}")
            return ""
    else:
        logging.info(f"No file found: {filename}.")
        return ""


# Write contents to a file
def write_file(content: str, filename: str) -> None:
    # Write the contents to a file
    try:
        with open(filename, "w") as file:
            file.write(content)
        logging.info(f"Contents written to {filename}")
    except Exception as e:
        logging.error(f"Failed to write contents to file: {e}")


# Parse the date with a possible list of formats
def parse_date(date_string: str) -> datetime:
    # List of possible date formats
    date_formats = [
        "%Y-%m-%d %H:%M:%S",  # Example: 2024-11-11 11:18:15
        "%Y:%m:%d %H:%M:%S",  # Example: 2024:11:11 11:18:15
        "%d-%m-%Y %H:%M:%S",  # Example: 11-11-2024 11:18:15
        "%m/%d/%Y %H:%M:%S",  # Example: 11/11/2024 11:18:15
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f"Date format not supported: {date_string}")
