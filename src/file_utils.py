import logging
import os


# Read contents from file
def read_file(filename: str) -> str:
    # Check if the file exists
    if os.path.exists(filename):
        logging.info(f"Reading file {filename}...")
        try:
            with open(filename, "r") as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error reading file {filename}: {e}")
            return ""
    else:
        logging.info(f"No file found: {filename}.")
        return ""


# Write contents to a file
def write_file(content: str, filename: str) -> None:
    # Write the contents to a file
    try:
        with open(filename, "w") as file:
            file.write(content)
        logging.info(f"Contents written to {filename}")
    except Exception as e:
        logging.error(f"Failed to write contents to file: {e}")
