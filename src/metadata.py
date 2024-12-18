import os
import sys
import logging
import re
from markitdown import MarkItDown
from geopy.geocoders import AzureMaps
from utils import dms_to_decimal


# Extract metadata from an image file
def extract_metadata(image_file, client):
    try:
        # Create a MarkItDown instance to extract metadata from the image
        markitdown = MarkItDown()
        result = markitdown.convert(image_file)

        # Extract the date from the metadata
        date_pattern = r"DateTimeOriginal:\s*([^\n]+)"
        when_taken = re.search(date_pattern, result.text_content)
        if not when_taken:
            logging.warning(f"Date not found for {image_file}")
            return None

        logging.info(
            f"Extracted date: {when_taken.group(1)} from {os.path.basename(image_file)}"
        )

        # Extract the GPS position from the metadata
        gps_pattern = r"GPSPosition:\s*([^\n]+)"
        gps_position = re.search(gps_pattern, result.text_content)
        if not gps_position:
            logging.warning(f"GPS data not found for {image_file}")
            return None

        # Convert the GPS position to decimal coordinates
        decimal_coords = dms_to_decimal(gps_position.group(1))

        logging.info(
            f"Extracted GPS location: {decimal_coords[0]}, {decimal_coords[1]} from {os.path.basename(image_file)}"
        )

        # Reverse geocode the coordinates to get the location
        geolocator = AzureMaps(os.getenv("AZURE_MAPS_KEY"))
        location = geolocator.reverse(f"{decimal_coords[0]}, {decimal_coords[1]}")

        logging.info(
            f"Extracted location: {location} from {os.path.basename(image_file)}"
        )

        logging.info(
            f"Generating image summary for {os.path.basename(image_file)}..."
        )

        # Redirect stderr to suppress prompt logging from MarkItDown
        original_stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")

        # Create a MarkItDown instance to generate a description for the image
        markitdown_ai = MarkItDown(llm_client=client, llm_model="gpt-4o")
        result = markitdown_ai.convert(
            image_file,
            llm_prompt=f"""
                You are an individual looking back at a trip you have taken by reviewing the photographs.
                Write a paragraph for this image that describes the scene.
                Only use the latitude and longitude coordinates ({decimal_coords[0]},{decimal_coords[1]})
                and the town or city from the address ({location}) as a reference for it's geographic location.
                Do not include the coordinates in the output.
                Do include the name of the city or town the image is from.
                If you cannot determine the city or town then do not make it up just exclude it.
            """,
            llm_temperature=0.5,
        )

        # Restore stderr
        sys.stderr.close()
        sys.stderr = original_stderr

        # Extract the description from the AI-generated text
        description = ""
        description_pattern = r"# Description:\s*(.*)"
        description_match = re.search(
            description_pattern, result.text_content, re.DOTALL
        )
        if description_match:
            description = description_match.group(1).strip()
            logging.info(
                f"Generated summary: {description} from {os.path.basename(image_file)}"
            )

        # Return the extracted metadata
        return {
            "filename": os.path.basename(image_file),
            "location": {
                "latitude": decimal_coords[0],
                "longitude": decimal_coords[1],
                "address": location.address,
                "url": f"https://www.bing.com/maps?cp={decimal_coords[0]}~{decimal_coords[1]}&lvl=16",
            },
            "when": when_taken.group(1),
            "description": description,
        }
    except Exception as e:
        logging.error(f"Error processing {image_file}: {e}")
        return None
