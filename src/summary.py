import os
import logging
import re
from markitdown import MarkItDown
from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from openai import AzureOpenAI
from constants import GPT_MODEL, IMAGE_SUMMARY_TEMPERATURE
from typing import Any
from azure.core.exceptions import HttpResponseError
from trip_image import Address, TripImage
from PIL import Image
from PIL.ExifTags import TAGS


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


# Reverse geocode the coordinates to get the address data
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


# Convert degrees, minutes, seconds (DMS) coordinates to decimal degrees
def dms_to_decimal(dms):
    degrees, minutes, seconds = dms
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


# Extract metadata and generate a trip data for an image
def generate_trip_image_data(client: AzureOpenAI, image_path: str) -> TripImage:
    try:
        # Extract EXIF data from the image
        exif_data = extract_exif(image_path)

        # Get the date from the metadata
        when_taken = exif_data.get("DateTimeOriginal", None)
        if not when_taken:
            logging.warning(f"Date not found for {image_path}")
            return None

        logging.info(f"Extracted date: {when_taken} from {image_path}")

        # Get the GPS position from the metadata
        gps_data = exif_data.get("GPSInfo", None)
        if not gps_data:
            logging.warning(f"GPS data not found for {image_path}")
            return None

        # Convert the GPS position to decimal coordinates
        latitude_dms = gps_data[2]
        longitude_dms = gps_data[4]

        # Convert the GPS position to decimal coordinates
        latitude = dms_to_decimal(latitude_dms)
        longitude = dms_to_decimal(longitude_dms)

        # Check the direction of the coordinates
        latitude *= 1 if gps_data[1] == 'N' else -1
        longitude *= 1 if gps_data[3] == 'E' else -1
        logging.info(f"Extracted GPS information: {latitude}, {longitude} from {image_path}")

        # Reverse geocode the coordinates to get the location
        location = get_address(latitude, longitude)
        if not location:
            logging.warning(f"Location not found for coordinates: {latitude}, {longitude}")
            return None

        address = location.get('formattedAddress', None)
        logging.info(f"Extracted location: {address} from {image_path}")

        logging.info(f"Generating image summary for {image_path}...")

        # Create a MarkItDown instance to generate a description for the image
        markitdown_ai = MarkItDown(llm_client=client, llm_model=GPT_MODEL)
        exif_data = markitdown_ai.convert(
            image_path,
            llm_prompt=f"""
                You are an individual looking back at a trip you have taken by reviewing the photographs.
                Write a paragraph for this image that describes the scene.
                Only use the latitude and longitude coordinates ({latitude},{longitude})
                and the town or city from the address ({address}) as a reference for its geographic location.
                Do include the name of the city or town the image is from.
                If you cannot determine the city or town then do not make it up just exclude it.
                Do not end the paragraph with a full stop.
                Do not include the coordinates in the output.
            """,
            llm_temperature=IMAGE_SUMMARY_TEMPERATURE,
            max_tokens=200,
        )

        # Extract the description from the AI-generated text
        description = ""
        description_pattern = r"# Description:\s*(.*)"
        description_match = re.search(description_pattern, exif_data.text_content, re.DOTALL)

        if description_match:
            description = description_match.group(1).strip()
            logging.info(f"Generated summary: {description} from {image_path}")

        # Get the current working directory to remove from the image reference
        working_directory = os.getcwd()

        image_address = TripImage(
            filename=image_path.replace(working_directory, ""),
            address=Address(
                latitude=latitude,
                longitude=longitude,
                address=address,
                url=f"https://www.google.com/maps/place/{latitude},{longitude}",
            ),
            when=when_taken,
            caption=description,
        )

        # Return the trip image object
        return image_address
    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")
        return None
