# utils/iso_week_number.py

import logging

logger = logging.getLogger(__name__)

def iso_week_number(date_obj):
    """
    Calculate the ISO week number for a given date.
    ISO weeks start on Monday, and the first week has the year's first Thursday.

    Parameters:
    - date_obj (datetime): The date to calculate the ISO week number for.

    Returns:
    - int: The ISO week number.
    """
    try:
        week_num = date_obj.isocalendar()[1]
        logger.debug(f"ISO week number for {date_obj} is {week_num}.")
        return week_num
    except Exception as e:
        logger.error(f"Error calculating ISO week number: {e}")
        return None
