import logging
from typing import Any, List
from constants import (
    COLLATION_SYSTEM_PROMPT,
    COLLATION_USER_PROMPT,
    IMAGE_SUMMARY_TEMP,
    IMAGE_SYSTEM_PROMPT,
    IMAGE_USER_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    SUMMARY_USER_PROMPT,
    TRIP_SUMMARY_TEMP)
from open_ai import OpenAIClient
from trip_image import Address, Location, TripImage
from utils import (
    convert_dms_to_decimal,
    extract_exif_data,
    get_address,
    convert_local_image_to_data_url,
    serialise)


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
        latitude *= 1 if gps_data[1] == 'N' else -1
        longitude *= 1 if gps_data[3] == 'E' else -1
        logging.info(f"Extracted GPS information: {latitude}, {longitude} from {image_path}")

        # Reverse geocode the coordinates to get the location
        location = get_address(latitude, longitude, map_key)
        if not location:
            logging.warning(f"Location not found for coordinates: {latitude}, {longitude}")
            return None

        countryRegion = location.get('countryRegion', None)
        country = countryRegion.get('name', None)
        admin_districts = location.get('adminDistricts', None)
        iso = countryRegion.get('iso', None)

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
                    admin_districts=location.get('adminDistricts', None),
                    locality=location.get('locality', None),
                    formatted_address=location.get('formattedAddress', None)
                )
            ),
            date=when_taken
        )

        # Return the trip image object
        return image_data
    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")
        return None


# Generate a summary for the image
def generate_image_summary(ai_client: OpenAIClient, image: TripImage, context: str) -> str:
    try:
        logging.info(f"Generating image summary for {image['filename']}...")

        conversation = [
            {
                "role": "system",
                "content": IMAGE_SYSTEM_PROMPT.format(latitude=image['location']['latitude'],
                                                      longitude=image['location']['longitude'],
                                                      address=image['location']['address']),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": IMAGE_USER_PROMPT.format(context=context),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": convert_local_image_to_data_url(image['filename'])
                        },
                    },
                ],
                "temperature": IMAGE_SUMMARY_TEMP,
                "max_tokens": 250,
            },
        ]

        summary = ai_client.send_prompt(conversation)

        # Return the summary
        return summary
    except Exception as e:
        logging.error(f"Error generating image summary {image['filename']}: {e}")
        return None


# Generate a summary for the whole trip
def generate_trip_summary(ai_client: OpenAIClient, trip: Any, context: str) -> str:
    try:
        # Serialize the trip data to JSON
        trip_data_json = serialise(trip)

        logging.info(f"Generating trip summary for {trip['country']}...")

        conversation = [
            {
                "role": "system",
                "content": SUMMARY_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": SUMMARY_USER_PROMPT.format(trip_data_json=trip_data_json, context=context),
                "temperature": TRIP_SUMMARY_TEMP,
                "max_tokens": 500,
            },
        ]

        summary = ai_client.send_prompt(conversation)

        # Return the summary
        return summary
    except Exception as e:
        logging.error(f"Error generating trip summary {trip['country']}: {e}")
        return None


# Collate the image data into trips
def collate_trip(client: OpenAIClient, data: List[TripImage], context: str) -> str:
    # Serialize the trip data to JSON
    trip_data_json = serialise(data)

    # Define a conversation prompt to generate the markdown summary
    conversation = [
        {
            "role": "system",
            "content": f"{COLLATION_SYSTEM_PROMPT}",
        },
        {
            "role": "user",
            "content": COLLATION_USER_PROMPT.format(trip_data_json=trip_data_json, context=context),
            "temperature": 0,
        },
    ]

    logging.info("Collating image data into trips...")

    # Return the response from the OpenAI API
    return client.send_prompt(conversation)
