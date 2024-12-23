import os
import logging
from typing import List
from constants import (
    IMAGE_SUMMARY_TEMP,
    IMAGE_SYSTEM_PROMPT,
    MARKDOWN_TEMPLATE,
    SUMMARY_SYSTEM_PROMPT,
    SUMMARY_USER_PROMPT,
    TRIP_SUMMARY_TEMP)
from utils import read_file
from open_ai import OpenAIClient
from trip_image import Address, TripImage
from utils import dms_to_decimal, extract_exif, get_address, local_image_to_data_url, serialise_object


# Generate a summary for an image
def generate_image_summary(ai_client: OpenAIClient, image_path: str, map_key: str) -> TripImage:
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
        location = get_address(latitude, longitude, map_key)
        if not location:
            logging.warning(f"Location not found for coordinates: {latitude}, {longitude}")
            return None

        address = location.get('formattedAddress', None)
        logging.info(f"Extracted location: {address} from {image_path}")

        logging.info(f"Generating image summary for {image_path}...")

        conversation = [
            {
                "role": "system",
                "content": IMAGE_SYSTEM_PROMPT.format(latitude=latitude, longitude=longitude, address=address)
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Create a summary for this image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": local_image_to_data_url(image_path)
                        },
                    },
                ],
                "temperature": IMAGE_SUMMARY_TEMP,
                "max_tokens": 200,
            },
        ]

        summary = ai_client.send_prompt(conversation)

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
            caption=summary.rstrip('.'),
        )

        # Return the trip image object
        return image_address
    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")
        return None


# Generate an overall summary from the trip data
def generate_trip_summary(ai_client: OpenAIClient, trip_data: List[TripImage], full_path: str) -> str:
    # Read the context file to provide additional information
    context_file = os.path.join(full_path, "context.txt")
    context = read_file(context_file)

    # Serialize the trip data to JSON
    trip_data_json = serialise_object(trip_data)

    # Define a conversation prompt to generate the markdown summary
    conversation = [
        {
            "role": "system",
            "content": f"{SUMMARY_SYSTEM_PROMPT}{MARKDOWN_TEMPLATE}",
        },
        {
            "role": "user",
            "content": SUMMARY_USER_PROMPT.format(trip_data_json=trip_data_json, context=context),
            "temperature": TRIP_SUMMARY_TEMP,
        },
    ]

    # Generate the summary using the Azure OpenAI API
    logging.info("Creating trip summary...")

    # Return the response from the OpenAI API
    return ai_client.send_prompt(conversation)
