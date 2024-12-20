# A class to represent an address
class Address:
    def __init__(self, latitude: float, longitude: float, address: str, url: str):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.address: str = address
        self.url: str = url

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "url": self.url
        }


# A class to represent a trip image
class TripImage:
    def __init__(self, filename: str, address: Address, when: str, caption: str):
        self.filename: str = filename
        self.address: Address = address
        self.when: str = when
        self.caption: str = caption

    def to_dict(self):
        return {
            "filename": self.filename,
            "address": self.address.to_dict(),
            "when": self.when,
            "caption": self.caption
        }
