import os
import sys
import glob
import json
import argparse
import logging
from openai import AzureOpenAI
from dotenv import load_dotenv
from utils import MaskSensitiveDataFilter
from metadata import extract_metadata

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Add filter to mask sensitive data
logging.getLogger().addFilter(MaskSensitiveDataFilter())


# Parse images from a specified directory for metadata
def parse_image_metadata(directory, ai_client):
    metadata_output = []

    # Find all image files in the directory
    image_file_pattern = os.path.join(directory, "**", "*.jpg")
    image_files = glob.glob(image_file_pattern, recursive=True)

    # Iterate over each image file and extract metadata
    for image in image_files:
        logging.info(f"Processing {os.path.basename(image)}...")

        # Extract metadata from the image
        image_metadata = extract_metadata(image, ai_client)

        # If metadata is found, add it to the output
        if image_metadata:
            metadata_output.append(image_metadata)

    # Return the metadata output
    return metadata_output


# Main function
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Parse images from a specified path.")

    # Add argument for the path to the directory containing images
    parser.add_argument(
        "path", type=str, help="The path to the directory containing images"
    )
    args = parser.parse_args()
    directory = args.path

    # Check if the directory value has been provided
    if not directory:
        parser.error("The path to the directory containing images must be provided.")

    # Check if the directory exists
    if not os.path.isdir(directory):
        parser.error(f"The directory '{directory}' does not exist.")

    # Check if Azure OpenAI environment variables are set
    if not os.getenv("AZURE_OPENAI_ENDPOINT") or not os.getenv("AZURE_OPENAI_API_KEY"):
        logging.error("Azure OpenAI environment variables not set.")
        sys.exit(1)

    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-08-01-preview",
    )

    # Parse image metadata
    logging.info("Parsing image metadata...")
    image_data = parse_image_metadata(directory, client)

    logging.info("Sorting images by date taken...")
    sorted_by_date = sorted(image_data, key=lambda x: x["when"])

    # Define a conversation prompt to generate the markdown summary
    conversation = [
        {
            "role": "system",
            "content": """
                You are a helpful travel writing assistant creating a summary of trips from descriptions of each image.
                Create the output in markdown format and only output the markdown content.
                The markdown created must follow these rules:
                - Contain a top-level heading with the year or year span of the trips.
                - Order the trips chronologically by date taken of all images for that trip to a country within now more
                then a fourteen day period and create a separate sub-heading and section for each trip.
                - Create sub-headings for each trip with the country of the location and the dates of that trip.
                - Every trip must include, below the sub-heading, a summary of the entire trip to that location
                referencing all the images. This summary should be descriptive and more than a single sentence.
                - Do not include the word Summary in the output or as a heading.
                - The image itself.
                - The single sentence description of the image as a caption that includes the date and location it was
                taken as well as a URL to the location on a map as provided in the JSON data.
                - Do not include the word caption in the image caption.
                - Do not surround the image caption with quotation marks.
                - Do not begin the image caption with 'This image shows'.
                - Do not format the image caption using a bullet point or list.
                """,
        },
        {
            "role": "user",
            "content": f"""
            Given the following JSON journey data, collate information from each country and trip to create a summary
            of each trip.
            ```json
            {json.dumps(sorted_by_date, indent=4)}
            ```
        """,
        },
    ]

    # Generate the summary using the Azure OpenAI API
    logging.info("Generating summary of trips...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation,
    )

    # Extract the completion text from the response
    completion_text = response.choices[0].message.content

    # Write the markdown summary to a markdown file
    output_markdown_file = os.path.join(directory, "summary.md")
    with open(output_markdown_file, "w") as file:
        file.write(completion_text)


# Entry point of the script
if __name__ == "__main__":
    main()
