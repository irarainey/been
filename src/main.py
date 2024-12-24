import os
import sys
import glob
import argparse
import logging
from dotenv import load_dotenv
from datetime import datetime
from constants import GPT_API_VERSION, OUTPUT_DIR
from locations import get_location_data
from markdown import generate_markdown
from trips import collate_trips
from utils import read_file, serialise, write_file
from open_ai import OpenAIClient
from summaries import generate_image_summary, generate_trip_summary
from typing import List
from data_models import TripImage


# Main function
def main() -> None:
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Parse command-line arguments
    args_parser = argparse.ArgumentParser(
        description="Parse images from a specified path."
    )

    # Add argument for the path to the directory containing images
    args_parser.add_argument(
        "path", type=str, help="The path to the directory containing images"
    )
    args = args_parser.parse_args()
    image_directory = args.path

    # Ensure directory does not start with a slash
    image_directory = image_directory.lstrip("/")

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

    # Parse image metadata
    logging.info("Processing trip images...")
    images: List[TripImage] = []

    # Find all image files in the directory
    image_file_pattern = os.path.join(full_path, "**", "*.jpg")
    image_files = glob.glob(image_file_pattern, recursive=True)

    # Iterate over each image file in the directory
    for image in image_files:
        basename = os.path.basename(image)
        logging.info(f"Processing {basename}...")

        # Get location data for the image
        trip_image = get_location_data(image, os.getenv("AZURE_MAPS_KEY"))

        # Add the image to the list if it was successfully processed
        if trip_image:
            images.append(trip_image)

    # Collate the images into trips
    collated_trips = collate_trips(images)

    # Generate the summary using the Azure OpenAI API
    logging.info("Generating summary of each trip...")

    # Read the context file to provide additional information
    context_file = os.path.join(full_path, "context.txt")
    context = read_file(context_file)

    # Create an instance of the Azure OpenAI client
    ai_client = OpenAIClient(
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_API_KEY"),
        GPT_API_VERSION,
    )

    # Iterate over each trip and generate a summary
    for trip in collated_trips:
        logging.info(f"Processing trip to {trip.country}...")

        # Generate a summary for each image in the trip
        for image in trip.images:
            image_summary_content = generate_image_summary(ai_client, image, context)
            image.caption = image_summary_content

        # Generate a summary for the trip overall
        trip_summary_content = generate_trip_summary(ai_client, trip, context)
        trip.summary = trip_summary_content

    # Generate the markdown summary
    logging.info("Generating markdown for all trips...")
    markdown = generate_markdown(collated_trips)

    # Serialise the trip data to JSON
    trip_data_json = serialise(collated_trips)

    # Get the current timestamp to create a filename
    output_filename = f"summary_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Write the summary to a markdown file
    write_file(markdown, os.path.join(OUTPUT_DIR, f"{output_filename}.md"))

    # Write the JSON data to a file
    write_file(trip_data_json, os.path.join(OUTPUT_DIR, f"{output_filename}.json"))

    # And we're done!
    logging.info("Complete! Summary of trips generated successfully")


# Entry point of the script
if __name__ == "__main__":
    main()
