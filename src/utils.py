import os
import json
import base64
import logging
from PIL import Image
from typing import Any, List
from PIL.ExifTags import TAGS
from mimetypes import guess_type
from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from azure.core.exceptions import HttpResponseError


# Serialise an object to JSON
def serialise_object(objects: List[Any]) -> str:
    # Convert each object instance to a dictionary
    obj_dict = [obj.to_dict() for obj in objects]

    # Serialize the list of dictionaries to JSON
    obj_json = json.dumps(obj_dict, indent=4)

    return obj_json


# Convert degrees, minutes, seconds (DMS) coordinates to decimal degrees
def dms_to_decimal(dms: Any) -> float:
    degrees, minutes, seconds = dms
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


# Extract EXIF data from an image file
def extract_exif(image_path: str) -> dict:
    # Open the image file
    image = Image.open(image_path)

    # Extract EXIF data
    exif_data = image._getexif()

    # Convert EXIF data to a readable format
    exif_dict = {}
    if exif_data is not None:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            exif_dict[tag_name] = value

    return exif_dict


# Reverse geocode the coordinates to get the address data from Azure Maps
def get_address(latitude: float, longitude: float, map_key: str) -> Any:
    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(map_key))
    try:
        result = maps_search_client.get_reverse_geocoding(coordinates=[longitude, latitude])
        if result.get('features', False):
            props = result['features'][0].get('properties', {})
            if props and props.get('address', False):
                logging.info(props['address'])
                return props['address']
            else:
                logging.info("Address is None")
                return None
        else:
            logging.info("No features available")
            return None
    except HttpResponseError as exception:
        if exception.error is not None:
            logging.error(f"Error Code: {exception.error.code} - {exception.error.message}")
        return None


# Convert a local image to a data URL
def local_image_to_data_url(image_path: str) -> str:
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
