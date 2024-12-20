import json
import logging
import os
from typing import Any, List
from PIL import Image
from PIL.ExifTags import TAGS
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
def dms_to_decimal(dms):
    degrees, minutes, seconds = dms
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


# Extract EXIF data from an image file
def extract_exif(image_path):
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
def get_address(latitude, longitude) -> Any:
    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(os.getenv("AZURE_MAPS_KEY")))
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
