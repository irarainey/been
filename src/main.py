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
def write_markdown_summary(content):
    # Get the current timestamp current_timestamp
    current_timestamp = datetime.now()

    # Format the timestamp
    formatted_timestamp = current_timestamp.strftime("%Y%m%d%H%M%S")
    filename = f"summary_{formatted_timestamp}.md"
    markdown_file = os.path.join("output", filename)
    with open(markdown_file, "w") as file:
        file.write(content)


# Main function
def main():
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
    directory = args.path

    # Get the current base directory to create a full path
    working_directory = os.getcwd()
    full_path = f"{working_directory}{directory}"

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
    client = create_open_ai_client(os.getenv("AZURE_OPENAI_ENDPOINT"),
                                   os.getenv("AZURE_OPENAI_API_KEY"),
                                   GPT_API_VERSION)

    # Parse image metadata
    logging.info("Parsing image metadata...")
    image_data = process_images(client, full_path)

    logging.info("Sorting images by date taken...")
    sorted_by_date = sorted(image_data, key=lambda x: x["when"])

    # Generate the summary using the Azure OpenAI API
    logging.info("Generating summary of trips...")
    markdown_content = generate_trip_summary(client, sorted_by_date, full_path)

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
