import logging

logger = logging.getLogger(__name__)


def process_trailer_container_count(json_data):
    """
    Processes trailer container count data from JSON.
    Returns a dictionary mapping TrailerID to container counts.

    Parameters:
    - json_data (dict): JSON data containing trailer container counts.

    Returns:
    - dict: Dictionary mapping TrailerID to container counts.
    """
    try:
        trailer_map = json_data.get("ret", {}).get("trailerContainerCountMap", {})
        result = {}
        for trailer_id, counts in trailer_map.items():
            container_counts = counts.get("containerTypeToContainerCountMap", {})
            totes = container_counts.get("TOTE", 0)
            cartons = container_counts.get("CASE", 0)
            result[trailer_id] = {
                "Totes": totes,
                "Cartons": cartons
            }
        logger.debug(f"Processed trailer container count map: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing trailer container count data: {e}")
        logger.debug("Exception details:", exc_info=True)
        return {}