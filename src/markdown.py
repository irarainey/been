import os
from typing import Any
from datetime import datetime
from constants import MAP_BASE
from utils import read_file


# Generate markdown for the trips summary
def generate_markdown(trip_data: Any) -> str:
    working_directory = os.getcwd()
    full_path = os.path.join(working_directory, "resources/templates")

    # Open the markdown file templates and iterate through the trip data to populate the templates
    header_template = read_file(f"{full_path}/header.md")
    trip_template = read_file(f"{full_path}/trip.md")
    image_template = read_file(f"{full_path}/image.md")
    footer_template = read_file(f"{full_path}/footer.md")

    # Get first object in trip_data
    date_from = datetime.strptime(trip_data[0]["date_from"], "%Y-%m-%d %H:%M:%S")

    # Get last object in trip_data
    date_to = datetime.strptime(trip_data[-1]["date_to"], "%Y-%m-%d %H:%M:%S")

    # Calculate the year or year range between date_from and date_to
    if date_from.year == date_to.year:
        year = date_from.year
    else:
        year = f"{date_from.year}-{date_to.year}"

    # Header
    header_output = header_template.replace("{{ year }}", f"{year}")

    # Start with an empty trip
    trip_output = ""
    base_path = os.getcwd()

    # Iterate over each trip
    for trip in trip_data:
        # Start with an empty trip
        this_trip = ""
        this_trip = trip_template.replace("{{ iso-county-code }}",
                                          f"{str(trip['images'][0]['location']['address']['iso']).lower()}")
        this_trip = this_trip.replace("{{ country }}", f"{trip['country']}")
        this_trip = this_trip.replace("{{ location }}", f"{trip['images'][0]['location']['address']['locality']}")
        this_trip = this_trip.replace("{{ trip-summary }}", f"{trip['summary']}")
        this_trip = this_trip.replace("{{ date-range }}", f"{trip['date_from']} - {trip['date_to']}")

        # Start with no images
        this_trip_images = ""

        # Generate a summary for each image in the trip
        for image in trip["images"]:
            image_path = str(image["filename"]).replace(base_path, "")
            this_image = image_template.replace("{{ image-path }}", image_path)
            this_image = this_image.replace("{{ image-caption }}", str(image["caption"]).rstrip("."))
            this_image = this_image.replace(
                "{{ map-url }}", f"{MAP_BASE}{image['location']['latitude']},{image['location']['longitude']}")

            # Add the image to the trip
            this_trip_images += this_image + "\n"

        # Add the trip to the markdown output
        trip_output += this_trip + "\n" + this_trip_images + "\n"

    # Footer
    footer_output = footer_template

    # Return the markdown output
    return header_output + trip_output + footer_output
