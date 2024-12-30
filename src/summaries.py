import logging
from constants import (
    IMAGE_SUMMARY_TEMP,
    IMAGE_SYSTEM_PROMPT,
    IMAGE_USER_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    SUMMARY_USER_PROMPT,
    TRIP_SUMMARY_TEMP,
)
from gpt_client import OpenAIClient
from data_models import Trip, TripImage
from phi_client import PhiClient
from utils import convert_local_image_to_data_url, serialise


# Generate a summary for the image
def generate_image_summary(
    client: OpenAIClient, image: TripImage, context: str
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

        summary = client.send_prompt(conversation)

        # Return the summary
        return summary
    except Exception as e:
        logging.error(f"Error generating image summary {image.filename}: {e}")
        return None


# Generate a summary for the whole trip using GPT
def generate_gpt_trip_summary(client: OpenAIClient, trip: Trip, context: str) -> str:
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

        summary = client.send_prompt(conversation)

        # Return the summary
        return summary
    except Exception as e:
        logging.error(f"Error generating trip summary {trip.country}: {e}")
        return None


# Generate a summary for the whole trip using a phi model
def generate_phi_trip_summary(client: PhiClient, trip: Trip, context: str) -> str:
    try:
        # Serialize the trip data to JSON
        trip_data_json = serialise(trip)

        logging.info(f"Generating trip summary for {trip.country}...")

        conversation = {
            "messages": [
                {
                    "role": "system",
                    "content": SUMMARY_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": SUMMARY_USER_PROMPT.format(
                        trip_data_json=trip_data_json, context=context
                    )
                },
            ],
            "temperature": TRIP_SUMMARY_TEMP,
            "top_p": 0.1,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "max_tokens": 500,
        }

        summary = client.send_prompt(conversation)

        # Return the summary
        return summary
    except Exception as e:
        logging.error(f"Error generating trip summary {trip.country}: {e}")
        return None
