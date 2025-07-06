# utils/parse_json_response.py

import logging
import json

logger = logging.getLogger(__name__)

def parse_json_response(response_text):
    """
    Parses the JSON response.

    Parameters:
    - response_text (str): The response text to parse.

    Returns:
    - dict: The parsed JSON object, or None if parsing fails.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        logger.debug(f"Response text that failed to parse: {response_text}")
        return None
