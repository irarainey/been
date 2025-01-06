# OpenAI constants
GPT_MODEL = "gpt-4o"
GPT_API_VERSION = "2024-08-01-preview"

# System prompt for the image description call
IMAGE_SYSTEM_PROMPT = """
    You are an individual looking back at a trip you have taken by reviewing your photographs.
    Write a paragraph for this image that describes the scene.
    Only use the latitude and longitude coordinates ({latitude},{longitude}) and the town or \
    city from the address ({address}) as a reference for its geographic location.
    If you cannot determine the city or town then do not make it up just exclude it.
    Do not include the coordinates in the output.
    Do not include the address or the name of the city or the town in the summary.
    Do not start the output with 'This image' or 'This photo' or 'This photograph'.
    Only output plain text.
    """

# User prompt for the image description call
IMAGE_USER_PROMPT = """
    Create a summary description for this image.
    Use the additional context delimited by triple backticks where relevant for information to describe the image \
    as part of a trip:
    ```
    {context}
    ```
    """

# System prompt for the overall summary call
SUMMARY_SYSTEM_PROMPT = """
    You are an individual looking back at all trips you have taken and writing a journal summary from descriptions \
    of each image and relevant geographic and historic country information.
    Create an overall summary of each trip taken by combining the caption from each image any relevant geographical \
    or historical country information together with any additional context for that trip as provided.
    Only output a summary for each trip as a single paragraph.
    Only output plain text.
    Do not include the image captions.
    Do not duplicate information that is already in the image captions.
    """

# User prompt for the overall summary call
SUMMARY_USER_PROMPT = """
    Collate information from each image caption to create a summary of each trip using the the JSON journey data \
    delimited by triple exclamation marks.
    !!!
    {trip_data_json}
    !!!
    Use the additional context delimited by triple backticks where relevant for information to describe the image \
    as part of a trip:
    ```
    {context}
    ```
    """

# Image summary temperature
IMAGE_SUMMARY_TEMP = 0.2

# Trip summary temperature
TRIP_SUMMARY_TEMP = 0.2

# Output directory
OUTPUT_DIR = "output"

# Google Maps base URL
MAP_BASE = "https://www.google.com/maps/place/"
