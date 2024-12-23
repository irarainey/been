import os
import sys
import glob
import argparse
import logging
from dotenv import load_dotenv
from datetime import datetime
from constants import GPT_API_VERSION, OUTPUT_DIR
from utils import write_file
from open_ai import OpenAIClient
from summaries import generate_image_summary, generate_trip_summary
from typing import List
from trip_image import TripImage
from utils import serialise_objects


# Main function
def main() -> None:
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Parse command-line arguments
    args_parser = argparse.ArgumentParser(description="Parse images from a specified path.")

    # Add argument for the path to the directory containing images
    args_parser.add_argument(
        "path", type=str, help="The path to the directory containing images"
    )
    args = args_parser.parse_args()
    image_directory = args.path

    # Ensure directory does not start with a slash
    image_directory = image_directory.lstrip('/')

    # Get the current base directory to create a full path
    working_directory = os.getcwd()
    full_path = os.path.join(working_directory, image_directory)

    logging.info(f"Processing images in directory: {full_path}...")

    # Check if the directory exists
    if not os.path.isdir(full_path):
        args_parser.error(f"The path '{full_path}' does not exist.")

    # Load environment variables
    load_dotenv()

    # Check if Azure OpenAI environment variables are set
    if (
        not os.getenv("AZURE_OPENAI_ENDPOINT")
        or not os.getenv("AZURE_OPENAI_API_KEY")
        or not os.getenv("AZURE_MAPS_KEY")
    ):
        logging.error("Required environment variables not set.")
        sys.exit(1)

    # Create an instance of the Azure OpenAI client
    try:
        ai_client = OpenAIClient(
            os.getenv("AZURE_OPENAI_ENDPOINT"),
            os.getenv("AZURE_OPENAI_API_KEY"),
            GPT_API_VERSION)
    except Exception as e:
        logging.error(f"Failed to create OpenAI client: {e}")
        sys.exit(1)

    # Parse image metadata
    logging.info("Processing trip images...")
    trip_images: List[TripImage] = []

    # Find all image files in the directory
    image_file_pattern = os.path.join(full_path, "**", "*.jpg")
    image_files = glob.glob(image_file_pattern, recursive=True)

    # Iterate over each image file in the directory
    for image in image_files:
        logging.info(f"Processing {os.path.basename(image)}...")

        # Extract metadata from the image and generate a summary
        try:
            trip_image = generate_image_summary(ai_client, image, os.getenv("AZURE_MAPS_KEY"))
        except Exception as e:
            logging.error(f"Failed to generate summary for {image}: {e}")
            continue

        # If summary is generated, add it to the trip summary list
        if trip_image:
            trip_images.append(trip_image)

    logging.info("Sorting trip data by date image taken...")
    sorted_by_date = sorted(trip_images, key=lambda x: x.when)

    # Generate the summary using the Azure OpenAI API
    logging.info("Generating overall summary of trips...")
    try:
        markdown_content = generate_trip_summary(ai_client, sorted_by_date, full_path)
    except Exception as e:
        logging.error(f"Failed to generate overal summary of trips: {e}")
        sys.exit(1)

    # Parse the markdown to update the image captions
    logging.info("Updating image captions...")
    for image in sorted_by_date:
        logging.info(f"Updating captions for {image.filename} to {image.caption}")
        markdown_content = markdown_content.replace(f"%{image.filename}%", f"{image.caption}")

    # Get the current timestamp
    current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"summary_{current_timestamp}"

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Write the markdown summary to a file
    write_file(markdown_content, os.path.join(OUTPUT_DIR, f"{output_filename}.md"))

    # Write the JSON data to a file
    trip_data_json = serialise_objects(sorted_by_date)
    write_file(trip_data_json, os.path.join(OUTPUT_DIR, f"{output_filename}.json"))

    # And we're done!
    logging.info("Complete! Summary of trips generated successfully")


# Entry point of the script
if __name__ == "__main__":
    main()
