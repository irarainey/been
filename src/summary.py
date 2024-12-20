import os
import logging
import re
from typing import List
from markitdown import MarkItDown
from constants import GPT_MODEL, IMAGE_SUMMARY_TEMP, MARKDOWN_TEMPLATE, SUMMARY_SYSTEM_PROMPT, TRIP_SUMMARY_TEMP
from file_utils import read_file
from open_ai import OpenAIClient
from trip_image import Address, TripImage
from utils import dms_to_decimal, extract_exif, get_address, serialise_object


# Extract metadata and generate a trip data for an image
def generate_trip_image_data(ai_client: OpenAIClient, image_path: str) -> TripImage:
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
        markitdown_ai = MarkItDown(llm_client=ai_client.client, llm_model=GPT_MODEL)
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
            llm_temperature=IMAGE_SUMMARY_TEMP,
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
            "content": f"""
                Given the following JSON journey data, collate information from each country and trip to create a
                summary of each trip.
                ```json
                {trip_data_json}
                ```
                Use this additional context to provide add information:
                ```text
                {context}
                ```
            """,
            "temperature": TRIP_SUMMARY_TEMP,
        },
    ]

    # Generate the summary using the Azure OpenAI API
    logging.info("Creating trip summary...")

    # Return the response from the OpenAI API
    return ai_client.send_prompt(conversation)
