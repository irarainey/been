import re
import logging


# Define a custom logging filter to mask sensitive data
class MaskSensitiveDataFilter(logging.Filter):
    def filter(self, record):
        if record.args:
            record.msg = re.sub(
                r"subscription-key=[^&]+", "subscription-key=***", record.msg
            )
        return True


# Convert degrees, minutes, seconds (DMS) coordinates to decimal degrees
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

        if direction in ["S", "W"]:
            decimal_degree = -decimal_degree

        decimal_coords.append(decimal_degree)

    return decimal_coords
