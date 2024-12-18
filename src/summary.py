import os
import sys
import logging
import re
from markitdown import MarkItDown
from geopy.geocoders import AzureMaps
from constants import GPT_MODEL, IMAGE_SUMMARY_TEMPERATURE
from typing import List, Dict, Any


# Reverse geocode the coordinates to get the location
def get_location(decimal_coords: List[float]) -> Any:
    try:
        maps = AzureMaps(os.getenv("AZURE_MAPS_KEY"))
        return maps.reverse(f"{decimal_coords[0]}, {decimal_coords[1]}")
    except Exception as e:
        logging.error(f"Failed to reverse geocode coordinates {decimal_coords}: {e}")
        return None


# Convert degrees, minutes, seconds (DMS) coordinates to decimal degrees
def dms_to_decimal(dms_str: str) -> List[float]:
    pattern = r"(\d+) deg (\d+)' (\d+\.?\d*)\"? ([NSEW])"
    matches = re.findall(pattern, dms_str)

    decimal_coords = []

    for match in matches:
        degrees, minutes, seconds, direction = match
        degrees = float(degrees)
        minutes = float(minutes) / 60
        seconds = float(seconds) / 3600

        decimal_degree = degrees + minutes + seconds

        if direction in ["S", "W"]:
            decimal_degree = -decimal_degree

        decimal_coords.append(decimal_degree)

    return decimal_coords


# Extract metadata and generate a summary for an image
def generate_image_summary(client: Any, image_path: str) -> Dict[str, Any]:
    try:
        # Create a MarkItDown instance to extract metadata from the image
        markitdown = MarkItDown()
        result = markitdown.convert(image_path)

        # Extract the date from the metadata
        date_pattern = r"DateTimeOriginal:\s*([^\n]+)"
        when_taken = re.search(date_pattern, result.text_content)
        if not when_taken:
            logging.warning(f"Date not found for {image_path}")
            return None

        logging.info(f"Extracted date: {when_taken.group(1)} from {image_path}")

        # Extract the GPS position from the metadata
        gps_pattern = r"GPSPosition:\s*([^\n]+)"
        gps_position = re.search(gps_pattern, result.text_content)
        if not gps_position:
            logging.warning(f"GPS data not found for {image_path}")
            return None

        # Convert the GPS position to decimal coordinates
        decimal_coords = dms_to_decimal(gps_position.group(1))

        logging.info(f"Extracted GPS location: {decimal_coords[0]}, {decimal_coords[1]} from {image_path}")

        # Reverse geocode the coordinates to get the location
        location = get_location(decimal_coords)
        if not location:
            logging.warning(f"Location not found for coordinates: {decimal_coords}")
            return None

        logging.info(f"Extracted location: {location} from {image_path}")

        logging.info(f"Generating image summary for {image_path}...")

        # Redirect stderr to suppress prompt logging from MarkItDown
        original_stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")

        # Create a MarkItDown instance to generate a description for the image
        markitdown_ai = MarkItDown(llm_client=client, llm_model=GPT_MODEL)
        result = markitdown_ai.convert(
            image_path,
            llm_prompt=f"""
                You are an individual looking back at a trip you have taken by reviewing the photographs.
                Write a paragraph for this image that describes the scene.
                Only use the latitude and longitude coordinates ({decimal_coords[0]},{decimal_coords[1]})
                and the town or city from the address ({location}) as a reference for its geographic location.
                Do include the name of the city or town the image is from.
                If you cannot determine the city or town then do not make it up just exclude it.
                Do not end the paragraph with a full stop.
                Do not include the coordinates in the output.
            """,
            llm_temperature=IMAGE_SUMMARY_TEMPERATURE,
            max_tokens=200,
        )

        # Restore stderr
        sys.stderr.close()
        sys.stderr = original_stderr

        # Extract the description from the AI-generated text
        description = ""
        description_pattern = r"# Description:\s*(.*)"
        description_match = re.search(description_pattern, result.text_content, re.DOTALL)

        if description_match:
            description = description_match.group(1).strip()
            logging.info(f"Generated summary: {description} from {image_path}")

        # Get the current working directory to remove from the image reference
        working_directory = os.getcwd()

        # Return the extracted metadata
        return {
            "filename": image_path.replace(working_directory, ""),
            "location": {
                "latitude": decimal_coords[0],
                "longitude": decimal_coords[1],
                "address": location.address,
                "url": f"https://www.bing.com/maps?cp={decimal_coords[0]}~{decimal_coords[1]}&lvl=16",
            },
            "when": when_taken.group(1),
            "caption": description,
        }
    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")
        return None
