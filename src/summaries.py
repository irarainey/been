import logging
from constants import (
    IMAGE_SUMMARY_TEMP,
    IMAGE_SYSTEM_PROMPT,
    IMAGE_USER_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    SUMMARY_USER_PROMPT,
    TRIP_SUMMARY_TEMP,
)
from open_ai import OpenAIClient
from data_models import Trip, TripImage
from utils import convert_local_image_to_data_url, serialise


# Generate a summary for the image
def generate_image_summary(
    ai_client: OpenAIClient, image: TripImage, context: str
) -> str:
    try:
        logging.info(f"Generating image summary for {image.filename}...")

        conversation = [
            {
                "role": "system",
                "content": IMAGE_SYSTEM_PROMPT.format(
                    latitude=image.location.latitude,
                    longitude=image.location.longitude,
                    address=image.location.address,
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": IMAGE_USER_PROMPT.format(context=context),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": convert_local_image_to_data_url(image.filename)
                        },
                    },
                ],
                "temperature": IMAGE_SUMMARY_TEMP,
                "max_tokens": 250,
            },
        ]

        summary = ai_client.send_prompt(conversation)

        # Return the summary
        return summary
    except Exception as e:
        logging.error(f"Error generating image summary {image.filename}: {e}")
        return None


# Generate a summary for the whole trip
def generate_trip_summary(ai_client: OpenAIClient, trip: Trip, context: str) -> str:
    try:
        # Serialize the trip data to JSON
        trip_data_json = serialise(trip)

        logging.info(f"Generating trip summary for {trip.country}...")

        conversation = [
            {
                "role": "system",
                "content": SUMMARY_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": SUMMARY_USER_PROMPT.format(
                    trip_data_json=trip_data_json, context=context
                ),
                "temperature": TRIP_SUMMARY_TEMP,
                "max_tokens": 500,
            },
        ]

        summary = ai_client.send_prompt(conversation)

        # Return the summary
        return summary
    except Exception as e:
        logging.error(f"Error generating trip summary {trip.country}: {e}")
        return None
