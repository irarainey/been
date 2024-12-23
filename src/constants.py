# OpenAI constants
GPT_MODEL = "gpt-4o"
GPT_API_VERSION = "2024-08-01-preview"

# System prompt for the image description call
IMAGE_SYSTEM_PROMPT = """
    You are an individual looking back at a trip you have taken by reviewing your photographs.
    Write a paragraph for this image that describes the scene.
    Only use the latitude and longitude coordinates ({latitude},{longitude})
    and the town or city from the address ({address}) as a reference for its geographic location.
    Do include the name of the city or town the image is from.
    If you cannot determine the city or town then do not make it up just exclude it.
    Do not include the coordinates in the output.
    Do not start the output with 'This image' or 'This photo' or 'This photograph'.
    """

# User prompt for the image description call
IMAGE_USER_PROMPT = """
    Create a summary description for this image.
    Use this additional context where relevant for information to describe the image as part of a trip:
    ```text
    {context}
    ```
    """

# System prompt for the overall summary call
SUMMARY_SYSTEM_PROMPT = """
    You are an individual looking back at all trips you have taken and writing a journal summary from descriptions
    of each image and relevant geographic and historic country information.
    Create an overall summary of each trip taken by combining the caption from each image any relevant geographical
    or historical country information together with any additional context for that trip as provided.
    Only output the summary for each trip and do not include the image captions.
    Output plain text only.
    """

# User prompt for the overall summary call
SUMMARY_USER_PROMPT = """
    Given the following JSON journey data, collate information from each image caption to create a
    summary of each trip.
    ```json
    {trip_data_json}
    ```
    Use this additional context where relevant to provide add information for the trip:
    ```text
    {context}
    ```
    """

# System prompt for the collation call
COLLATION_SYSTEM_PROMPT = """
    You are a JSON data processor. Process the supplied JSON to collate images into trips.
    Do not exclude any images from the output.
    Only output valid JSON data.
    All output must be in as an array of JSON data following the structure:
    ```json
    [
        {
        "country": "{country-name}",
        "date_from": "{start-of-date-range-of-trip}",
        "date_to": "{end-of-date-range-of-trip}",
        "summary": "",
        "images": [
            {
                "filename": "{image-filename}",
                "location": {
                    "latitude": {latitude},
                    "longitude": {longitude},
                    "address": {
                        "country": "{country-name}",
                        "iso": "{iso-code}",
                        "admin_districts": ["{admin-district}"],
                        "locality": "{locality}",
                        "formatted_address": "{formatted-address}"
                        },
                    },
                "date": "{date}"
                "caption": "",
            ]
        }
    ]
    ```
    The JSON must follow these rules:
    - Order the trips chronologically by date taken of all images for that trip to a country within no more
    than a fourteen day period and create a separate sub-heading and section for each trip.
    - Do not include ```json or ``` in the output. Only output the JSON data.
    - Format all dates in the JSON data as YYYY-MM-DD HH:MM:SS.
    """

# User prompt for the collation call
COLLATION_USER_PROMPT = """
    Using this JSON data, collate information from each trip to create an ordered collection of images per trip.
    ```json
    {trip_data_json}
    ```
    Use this additional context where relevant for information to collate trips:
    ```text
    {context}
    ```
    """

# Image summary temperature
IMAGE_SUMMARY_TEMP = 0.3

# Trip summary temperature
TRIP_SUMMARY_TEMP = 0.3

# Output directory
OUTPUT_DIR = "output"

# Google Maps base URL
MAP_BASE = "https://www.google.com/maps/place/"