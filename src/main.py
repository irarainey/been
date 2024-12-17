import re
import os
import sys
import glob
import json
import argparse
from openai import AzureOpenAI
from markitdown import MarkItDown
from geopy.geocoders import AzureMaps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Convert degrees, minutes, seconds to decimal degrees
def dms_to_decimal(dms_str):
    pattern = r"(\d+) deg (\d+)' (\d+\.?\d*)\"? ([NSEW])"
    matches = re.findall(pattern, dms_str)

    decimal_coords = []

    for match in matches:
        degrees, minutes, seconds, direction = match
        degrees = float(degrees)
        minutes = float(minutes) / 60
        seconds = float(seconds) / 3600

        decimal_degree = degrees + minutes + seconds

        if direction in ["S", "W"]:
            decimal_degree = -decimal_degree

        decimal_coords.append(decimal_degree)

    return decimal_coords


# Parse images in a directory to extract metadata
def parse_images(directory, client):

    markitdown = MarkItDown()
    markitdown_ai = MarkItDown(llm_client=client, llm_model="gpt-4o")
    output = []
    pattern = os.path.join(directory, "**", "*.jpg")
    jpg_files = glob.glob(pattern, recursive=True)

    for jpg_file in jpg_files:
        print(f"Processing {os.path.basename(jpg_file)}...")
        result = markitdown.convert(jpg_file)

        date_pattern = r"DateTimeOriginal:\s*([^\n]+)"
        when_taken = re.search(date_pattern, result.text_content)

        gps_pattern = r"GPSPosition:\s*([^\n]+)"
        gps_position = re.search(gps_pattern, result.text_content)
        decimal_coords = dms_to_decimal(gps_position.group(1))

        geolocator = AzureMaps(os.getenv("AZURE_MAPS_KEY"))
        location = geolocator.reverse(f"{decimal_coords[0]}, {decimal_coords[1]}")

        # Save the original stderr and redirect it to /dev/null to suppress prompt showing
        original_stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")

        result = markitdown_ai.convert(
            jpg_file,
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

        sys.stderr.close()
        sys.stderr = original_stderr

        description = ""
        pattern = r"# Description:\s*(.*)"
        match = re.search(pattern, result.text_content, re.DOTALL)
        if match:
            description = match.group(1).strip()

        output.append(
            {
                "filename": os.path.basename(jpg_file),
                "location": {
                    "latitude": decimal_coords[0],
                    "longitude": decimal_coords[1],
                    "address": location.address,
                    "url": f"https://www.bing.com/maps?cp={decimal_coords[0]}~{decimal_coords[1]}&lvl=16",
                },
                "when": when_taken.group(1),
                "description": description,
            }
        )

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse images from a specified path.")
    parser.add_argument(
        "path", type=str, help="The path to the directory containing images"
    )
    args = parser.parse_args()
    directory = args.path

    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-08-01-preview",
    )

    print("Parsing images...")
    image_data = parse_images(directory, client)

    print("Sorting images by date taken...")
    sorted_by_date = sorted(image_data, key=lambda x: x["when"])

    print("Creating summary of trips...")

    conversation = [
        {
            "role": "system",
            "content": "You are a helpful travel writing assistant. Only output the markdown content.",
        },
        {
            "role": "user",
            "content": f"""
            Given the following JSON journey data, collate information from each country and trip and create a summary of each trip.
            ```json
            {json.dumps(sorted_by_date, indent=4)}
            ```
            The markdown should contain:
            - A top-level heading with the year or years of the trips.
            - Chronologically order the trips by date taken of all images for that trip to that country and create a section for each trip.
            - If the date of the images in close geographic proximity span more than fourteen days then create a separate section for each trip.
            - Create sub-headings for the country of the location with the dates of that trip.
            - Every trip must inclulde, below the sub-heading, a summary of the entire trip to that location referencing all the images. This summary should be descriptive and more than a single sentence.
            - The image.
            - The single sentence description of the image as a caption that includes the date and location it was taken as well as a URL to the location on a map as provided in the JSON data. Do not include the word caption in the output.
            - Do not format the caption using a bullet point or list.
            Create the output in markdown format.
        """,
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation,
    )

    completion_text = response.choices[0].message.content

    output_file = f"{directory}/summary.md"
    with open(output_file, "w") as file:
        file.write(completion_text)
