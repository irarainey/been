import logging
from typing import List
from data_models import Trip, TripImage


# Collate the image data into trips
def collate_trips(data: List[TripImage]) -> List[Trip]:
    # Sort images by date taken
    logging.info("Sorting images by date taken...")
    sorted_images = sorted(data, key=lambda x: x.date)

    # Collate the images into trips
    logging.info("Collating images into trips...")
    trips: List[Trip] = []
    trip: Trip = None
    for image in sorted_images:
        if not trip:
            trip = create_new_trip(image)
            continue

        # Check if the country the image was taken in is the same as the last image and if not create a new trip
        if image.location.address.country == trip.country:
            # If the dates of the images are more than 14 days apart, create a new trip
            if (image.date - trip.date_to).days > 14:
                trips.append(trip)
                trip = create_new_trip(image)
            else:
                trip.images.append(image)
        else:
            trips.append(trip)
            trip = create_new_trip(image)

    # Add the last trip to the list
    trips.append(trip)

    # Return the response from the OpenAI API
    return trips


# Create a new trip with the specified image
def create_new_trip(image: TripImage) -> Trip:
    return Trip(
        country=image.location.address.country,
        date_from=image.date,
        date_to=image.date,
        images=[image],
    )
