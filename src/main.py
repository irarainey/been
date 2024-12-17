import re
import os
import glob
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

        if direction in ['S', 'W']:
            decimal_degree = -decimal_degree

        decimal_coords.append(decimal_degree)

    return decimal_coords


# Parse images in a directory to extract metadata
def parse_images(directory):
    markitdown = MarkItDown()
    output = []
    pattern = os.path.join(directory, '**', '*.jpg')
    jpg_files = glob.glob(pattern, recursive=True)

    for jpg_file in jpg_files:
        result = markitdown.convert(jpg_file)

        date_pattern = r"DateTimeOriginal:\s*([^\n]+)"
        when_taken = re.search(date_pattern, result.text_content)

        gps_pattern = r"GPSPosition:\s*([^\n]+)"
        gps_position = re.search(gps_pattern, result.text_content)
        decimal_coords = dms_to_decimal(gps_position.group(1))

        geolocator = AzureMaps(os.getenv("AZURE_MAPS_KEY"))
        location = geolocator.reverse(
            f"{decimal_coords[0]}, {decimal_coords[1]}")

        output.append({"filename": jpg_file,
                       "location": {
                           "latitude": decimal_coords[0],
                           "longitude": decimal_coords[1],
                           "address": location.address,
                       },
                       "when": when_taken.group(1)})

        sorted_by_date = sorted(output, key=lambda x: x["when"])
    return sorted_by_date


if __name__ == "__main__":

    image_data = parse_images("images")

    for item in image_data:
        print(item)
