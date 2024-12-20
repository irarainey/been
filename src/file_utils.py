import logging
import os


# Read contents from file
def read_file(full_path: str) -> str:
    # Check if the file exists
    if os.path.exists(full_path):
        logging.info("Reading file...")
        try:
            with open(full_path, "r") as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error reading file: {e}")
            return ""
    else:
        logging.info("No file found.")
        return ""


# Write contents to a file
def write_file(content: str, filename: str) -> None:
    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Format the timestamp
    markdown_file = os.path.join(output_dir, filename)

    # Write the contents to a file
    try:
        with open(markdown_file, "w") as file:
            file.write(content)
        logging.info(f"Contents written to {markdown_file}")
    except Exception as e:
        logging.error(f"Failed to write contents to file: {e}")
