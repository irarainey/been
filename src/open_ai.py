import json
import logging
import os
from openai import AzureOpenAI
from constants import GPT_MODEL, MARKDOWN_OUTPUT_TEMPLATE, SUMMARY_SYSTEM_PROMPT, TRIP_SUMMARY_TEMPERATURE


# Create an instance of the Azure OpenAI client
def create_open_ai_client(endpoint, key, version):
    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=version,
    )

    return client


# Generate a summary from the trip data
def generate_trip_summary(client, trip_data, full_path):

    # Check if a context.txt file exists in the same directory as the images and if so, read the contents
    context = ""
    logging.info(f"Checking for context file in directory: {full_path}...")
    context_file = os.path.join(full_path, "context.txt")
    if os.path.exists(context_file):
        logging.info("Reading context file...")
        with open(context_file, "r") as file:
            context = file.read()

    if not context:
        logging.info("No context file found.")

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
                {json.dumps(trip_data, indent=4)}
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
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=conversation,
    )

    return response.choices[0].message.content
