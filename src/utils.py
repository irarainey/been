import json
from typing import Any, List


# Serialise an object to JSON
def serialise_object(objects: List[Any]) -> str:
    # Convert each object instance to a dictionary
    obj_dict = [obj.to_dict() for obj in objects]

    # Serialize the list of dictionaries to JSON
    obj_json = json.dumps(obj_dict, indent=4)

    return obj_json
