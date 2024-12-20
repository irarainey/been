import logging
import os
from openai import AzureOpenAI
from constants import GPT_MODEL, MARKDOWN_OUTPUT_TEMPLATE, SUMMARY_SYSTEM_PROMPT, TRIP_SUMMARY_TEMPERATURE
from typing import List
from file_utils import read_file
from trip_image import TripImage
from utils import serialise_object


# Create an instance of the Azure OpenAI client
def create_open_ai_client(endpoint: str, key: str, version: str) -> AzureOpenAI:
    try:
        # Initialize the Azure OpenAI client
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=key,
            api_version=version,
        )
        return client
    except Exception as e:
        logging.error(f"Failed to create OpenAI client: {e}")
        raise


# Generate a summary from the trip data
def generate_trip_summary(client: AzureOpenAI, trip_data: List[TripImage], full_path: str) -> str:
    context_file = os.path.join(full_path, "context.txt")
    context = read_file(context_file)

    # Serialize the trip data to JSON
    trip_data_json = serialise_object(trip_data)

    # Define a conversation prompt to generate the markdown summary
    conversation = [
        {
            "role": "system",
            "content": f"{SUMMARY_SYSTEM_PROMPT}{MARKDOWN_OUTPUT_TEMPLATE}",
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
            "temperature": TRIP_SUMMARY_TEMPERATURE,
        },
    ]

    # Generate the summary using the Azure OpenAI API
    logging.info("Creating trip summary...")
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=conversation,
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Failed to generate trip summary: {e}")
        raise
