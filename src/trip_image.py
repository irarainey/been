# A class to represent an address
class Address:
    def __init__(self, country: str, iso: str, admin_districts: list, locality: str, formatted_address: str):
        self.country: str = country
        self.iso: str = iso
        self.admin_districts: list = admin_districts
        self.locality: str = locality
        self.formatted_address: str = formatted_address

    def to_dict(self):
        return {
            "country": self.country,
            "iso": self.iso,
            "admin_districts": self.admin_districts,
            "locality": self.locality,
            "formatted_address": self.formatted_address
        }


# A class to represent a location
class Location:
    def __init__(self, latitude: float, longitude: float, address: Address):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.address: Address = address

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address.to_dict()
        }


# A class to represent a trip image
class TripImage:
    def __init__(self, filename: str, location: Location, date: str, caption: str = ""):
        self.filename: str = filename
        self.date: str = date
        self.location: Location = location
        self.caption: str = caption

    def to_dict(self):
        return {
            "filename": self.filename,
            "date": self.date,
            "location": self.location.to_dict(),
            "caption": self.caption
        }
