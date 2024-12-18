import os
import sys
import glob
import argparse
import logging
from dotenv import load_dotenv
from logging_filter import MaskSensitiveDataFilter
from constants import GPT_API_VERSION, OUTPUT_MARKDOWN_FILE
from open_ai import create_open_ai_client, generate_trip_summary
from summary import generate_image_summary


# Process images from a specified directory for metadata and generate a summary
def process_images(client, directory):
    trip_summaries = []

    # Find all image files in the directory
    image_file_pattern = os.path.join(directory, "**", "*.jpg")
    image_files = glob.glob(image_file_pattern, recursive=True)

    # Iterate over each image file in the directory
    for image in image_files:
        logging.info(f"Processing {os.path.basename(image)}...")

        # Extract metadata from the image and generate a summary
        image_summary = generate_image_summary(client, image)

        # If summary is generated, add it to the trip summary list
        if image_summary:
            trip_summaries.append(image_summary)

    # Return the trip summary list
    return trip_summaries


# Write the markdown summary to a file
def write_markdown_summary(directory, content):
    markdown_file = os.path.join(directory, OUTPUT_MARKDOWN_FILE)
    with open(markdown_file, "w") as file:
        file.write(content)


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

    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Add filter to mask sensitive data
    logging.getLogger().addFilter(MaskSensitiveDataFilter())

    # Load environment variables
    load_dotenv()

    # Check if Azure OpenAI environment variables are set
    if (
        not os.getenv("AZURE_OPENAI_ENDPOINT")
        or not os.getenv("AZURE_OPENAI_API_KEY")
        or not os.getenv("AZURE_MAPS_KEY")
    ):
        logging.error("Azure OpenAI environment variables not set.")
        sys.exit(1)

    # Create an instance of the Azure OpenAI client
    client = create_open_ai_client(os.getenv("AZURE_OPENAI_ENDPOINT"),
                                   os.getenv("AZURE_OPENAI_API_KEY"),
                                   GPT_API_VERSION)

    # Parse image metadata
    logging.info("Parsing image metadata...")
    image_data = process_images(client, directory)

    logging.info("Sorting images by date taken...")
    sorted_by_date = sorted(image_data, key=lambda x: x["when"])

    # Generate the summary using the Azure OpenAI API
    logging.info("Generating summary of trips...")
    markdown_content = generate_trip_summary(client, sorted_by_date)

    # Write the markdown summary to a file
    write_markdown_summary(directory, markdown_content)

    # And we're done!
    logging.info("Complete! Markdown summary generated successfully")


# Entry point of the script
if __name__ == "__main__":
    main()
