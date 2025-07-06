import logging

logger = logging.getLogger(__name__)


def process_load_fullness(json_data):
    """
    Processes load fullness data from JSON.
    Returns a dictionary mapping PlanId to availableCapacityPercentage.

    Parameters:
    - json_data (dict): JSON data containing load fullness information.

    Returns:
    - dict: Dictionary mapping vrId to availableCapacityPercentage.
    """
    try:
        load_fullness_map = json_data.get("ret", {}).get("loadFullnessMap", {})
        result = {}
        for plan_id, details in load_fullness_map.items():
            percentage = details.get("extendedFullnessDetails", {}).get("availableCapacityPercentage", "null")
            result[plan_id] = percentage
        logger.debug(f"Processed load fullness map: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing load fullness data: {e}")
        logger.debug("Exception details:", exc_info=True)
        return {}

