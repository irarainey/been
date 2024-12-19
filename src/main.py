import os
import sys
import glob
import argparse
import logging
from dotenv import load_dotenv
from datetime import datetime
from constants import GPT_API_VERSION
from open_ai import create_open_ai_client, generate_trip_summary
from summary import generate_image_summary
from typing import List, Dict, Any


# Process images from a specified directory for metadata and generate a summary
def process_images(client, directory: str) -> List[Dict[str, Any]]:
    trip_summaries = []

    # Find all image files in the directory
    image_file_pattern = os.path.join(directory, "**", "*.jpg")
    image_files = glob.glob(image_file_pattern, recursive=True)

    # Iterate over each image file in the directory
    for image in image_files:
        logging.info(f"Processing {os.path.basename(image)}...")

        # Extract metadata from the image and generate a summary
        try:
            image_summary = generate_image_summary(client, image)
        except Exception as e:
            logging.error(f"Failed to generate summary for {image}: {e}")
            continue

        # If summary is generated, add it to the trip summary list
        if image_summary:
            trip_summaries.append(image_summary)

    # Return the trip summary list
    return trip_summaries


# Write the markdown summary to a file
def write_markdown_summary(content: str) -> None:
    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Get the current timestamp
    current_timestamp = datetime.now()

    # Format the timestamp
    formatted_timestamp = current_timestamp.strftime("%Y%m%d%H%M%S")
    filename = f"summary_{formatted_timestamp}.md"
    markdown_file = os.path.join(output_dir, filename)

    try:
        with open(markdown_file, "w") as file:
            file.write(content)
        logging.info(f"Markdown summary written to {markdown_file}")
    except Exception as e:
        logging.error(f"Failed to write markdown summary: {e}")


# Main function
def main() -> None:
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Parse images from a specified path.")

    # Add argument for the path to the directory containing images
    parser.add_argument(
        "path", type=str, help="The path to the directory containing images"
    )
    args = parser.parse_args()
    image_directory = args.path

    # Ensure directory does not start with a slash
    image_directory = image_directory.lstrip('/')

    # Get the current base directory to create a full path
    working_directory = os.getcwd()
    full_path = os.path.join(working_directory, image_directory)

    logging.info(f"Processing images in directory: {full_path}...")

    # Check if the directory exists
    if not os.path.isdir(full_path):
        parser.error(f"The path '{full_path}' does not exist.")

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
    try:
        client = create_open_ai_client(os.getenv("AZURE_OPENAI_ENDPOINT"),
                                       os.getenv("AZURE_OPENAI_API_KEY"),
                                       GPT_API_VERSION)
    except Exception as e:
        logging.error(f"Failed to create OpenAI client: {e}")
        sys.exit(1)

    # Parse image metadata
    logging.info("Parsing image metadata...")
    image_data = process_images(client, full_path)

    logging.info("Sorting images by date taken...")
    sorted_by_date = sorted(image_data, key=lambda x: x["when"])

    # Generate the summary using the Azure OpenAI API
    logging.info("Generating summary of trips...")
    try:
        markdown_content = generate_trip_summary(client, sorted_by_date, full_path)
    except Exception as e:
        logging.error(f"Failed to generate trip summary: {e}")
        sys.exit(1)

    # Parse the markdown to update the image captions
    logging.info("Updating image captions...")
    for image in sorted_by_date:
        logging.info(f"Updating captions for {image['filename']} to {image['caption']}")
        markdown_content = markdown_content.replace(f"%{image['filename']}%", f"{image['caption']}")

    # Write the markdown summary to a file
    write_markdown_summary(markdown_content)

    # And we're done!
    logging.info("Complete! Markdown summary generated successfully")


# Entry point of the script
if __name__ == "__main__":
    main()
