# yms_validation.py

import logging

logger = logging.getLogger(__name__)

def recursive_search(data, target: str) -> bool:
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, (dict, list)):
                if recursive_search(value, target):
                    return True
            elif isinstance(value, str) and value.strip() == target:
                return True
    elif isinstance(data, list):
        for item in data:
            if recursive_search(item, target):
                return True
    elif isinstance(data, str) and data.strip() == target:
        return True
    return False

def validate_yard_state(yard_state: dict, expected_value: str) -> bool:
    try:
        locations_summaries = yard_state.get("locationsSummaries", [])
        is_found = recursive_search(locations_summaries, expected_value)
        logger.info("Validation of yard state for expected value '%s': %s", expected_value, is_found)
        return is_found
    except Exception as e:
        logger.error("Exception during validate_yard_state: %s", str(e))
        return False
