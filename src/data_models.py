from datetime import datetime
from typing import List, Dict, Any


# Define the Address class
class Address:
    def __init__(
        self,
        country: str,
        iso: str,
        admin_district: str,
        locality: str,
        formatted_address: str,
    ):
        self.country: str = country
        self.iso: str = iso
        self.admin_district: str = admin_district
        self.locality: str = locality
        self.formatted_address: str = formatted_address

    def to_dict(self) -> Dict[str, Any]:
        return {
            "country": self.country,
            "iso": self.iso,
            "admin_district": self.admin_district,
            "locality": self.locality,
            "formatted_address": self.formatted_address,
        }


# Define the Location class
class Location:
    def __init__(self, latitude: float, longitude: float, address: Address):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.address: Address = address

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address.to_dict(),
        }


# Define the TripImage class
class TripImage:
    def __init__(
        self, filename: str, location: Location, date: datetime, caption: str = ""
    ):
        self.filename: str = filename
        self.date: datetime = date
        self.location: Location = location
        self.caption: str = caption

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "date": self.date.isoformat(),
            "location": self.location.to_dict(),
            "caption": self.caption,
        }


# Define the Trip class
class Trip:
    def __init__(
        self,
        country: str,
        date_from: datetime,
        date_to: datetime,
        images: List[TripImage],
        summary: str = "",
    ):
        self.country: str = country
        self.date_from: datetime = date_from
        self.date_to: datetime = date_to
        self.images: List[TripImage] = images
        self.summary: str = summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "country": self.country,
            "date_from": self.date_from.isoformat(),
            "date_to": self.date_to.isoformat(),
            "images": [image.to_dict() for image in self.images],
            "summary": self.summary,
        }
