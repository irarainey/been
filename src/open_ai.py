import json
from openai import AzureOpenAI
from constants import GPT_MODEL, SUMMARY_SYSTEM_PROMPT, TRIP_SUMMARY_TEMPERATURE


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
def generate_trip_summary(client, trip_data):
    # Define a conversation prompt to generate the markdown summary
    conversation = [
        {
            "role": "system",
            "content": SUMMARY_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"""
                Given the following JSON journey data, collate information from each country and trip to create a
                summary of each trip.
                ```json
                {json.dumps(trip_data, indent=4)}
                ```
            """,
            "temperature": TRIP_SUMMARY_TEMPERATURE,
        },
    ]

    # Generate the summary using the Azure OpenAI API
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=conversation,
    )

    return response.choices[0].message.content
