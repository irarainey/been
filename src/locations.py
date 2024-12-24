import logging
from PIL import Image
from typing import Any
from PIL.ExifTags import TAGS
from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from azure.core.exceptions import HttpResponseError
from data_models import Address, Location, TripImage
from utils import parse_date


# Convert degrees, minutes, seconds (DMS) coordinates to decimal degrees
def convert_dms_to_decimal(dms: Any) -> float:
    degrees, minutes, seconds = dms
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


# Extract EXIF data from an image file
def extract_exif_data(image_path: str) -> dict:
    # Open the image file
    image = Image.open(image_path)

    # Extract EXIF data
    exif_data = image._getexif()

    # Convert EXIF data to a readable format
    exif_dict = {}
    if exif_data is not None:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            exif_dict[tag_name] = value

    return exif_dict


# Reverse geocode the coordinates to get the address data from Azure Maps
def get_address(latitude: float, longitude: float, map_key: str) -> Any:
    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(map_key))
    try:
        result = maps_search_client.get_reverse_geocoding(
            coordinates=[longitude, latitude]
        )
        if result.get("features", False):
            props = result["features"][0].get("properties", {})
            if props and props.get("address", False):
                logging.info(props["address"])
                return props["address"]
            else:
                logging.info("Address is None")
                return None
        else:
            logging.info("No features available")
            return None
    except HttpResponseError as exception:
        if exception.error is not None:
            logging.error(
                f"Error Code: {exception.error.code} - {exception.error.message}"
            )
        return None


# Extract and generate location data for image
def get_location_data(image_path: str, map_key: str) -> TripImage:
    try:
        # Extract EXIF data from the image
        exif_data = extract_exif_data(image_path)

        # Get the date from the metadata
        when_taken = exif_data.get("DateTimeOriginal", None)
        if not when_taken:
            logging.warning(f"Date not found for {image_path}")
            return None

        logging.info(f"Extracted date: {when_taken} from {image_path}")

        # Get the GPS position from the metadata
        gps_data = exif_data.get("GPSInfo", None)
        if not gps_data:
            logging.warning(f"GPS data not found for {image_path}")
            return None

        # Convert the GPS position to decimal coordinates
        latitude_dms = gps_data[2]
        longitude_dms = gps_data[4]

        # Convert the GPS position to decimal coordinates
        latitude = convert_dms_to_decimal(latitude_dms)
        longitude = convert_dms_to_decimal(longitude_dms)

        # Check the direction of the coordinates
        latitude *= 1 if gps_data[1] == "N" else -1
        longitude *= 1 if gps_data[3] == "E" else -1
        logging.info(
            f"Extracted GPS information: {latitude}, {longitude} from {image_path}"
        )

        # Reverse geocode the coordinates to get the location
        location = get_address(latitude, longitude, map_key)
        if not location:
            logging.warning(
                f"Location not found for coordinates: {latitude}, {longitude}"
            )
            return None

        countryRegion = location.get("countryRegion", None)
        country = countryRegion.get("name", None)
        admin_districts = location.get("adminDistricts", None)
        iso = countryRegion.get("iso", None)

        # Ensure we get the right information for UK countries
        if admin_districts:
            for district in admin_districts:
                if "Wales" in district["name"]:
                    country = "Wales"
                    iso = "GB-WLS"
                    break
                elif "Scotland" in district["name"]:
                    country = "Scotland"
                    iso = "GB-SCT"
                    break
                elif "Northern Ireland" in district["name"]:
                    country = "Northern Ireland"
                    iso = "GB-NIR"
                    break

        image_data = TripImage(
            filename=image_path,
            location=Location(
                latitude=latitude,
                longitude=longitude,
                address=Address(
                    country=country,
                    iso=iso,
                    admin_district=admin_districts[0].get("name", None),
                    locality=location.get("locality", None),
                    formatted_address=location.get("formattedAddress", None),
                ),
            ),
            date=parse_date(when_taken),
        )

        # Return the trip image object
        return image_data
    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")
        return None
