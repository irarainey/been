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
