# utils/get_value_or_default.py

import logging

logger = logging.getLogger(__name__)

def get_value_or_default(attributes, key, default):
    """
    Helper function to get a value from attributes or return a default.

    Parameters:
    - attributes (dict): The dictionary to retrieve the value from.
    - key (str): The key to look for.
    - default: The default value to return if key is not found.

    Returns:
    - The value associated with the key or the default value.
    """
    return attributes.get(key, {}).get("value", default)
