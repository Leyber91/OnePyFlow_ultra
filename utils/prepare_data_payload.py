# utils/prepare_data_payload.py

import logging
from datetime import datetime
from utils.iso_week_number import iso_week_number

logger = logging.getLogger(__name__)

def prepare_data_payload(ws_start, csrf_token):
    """
    Prepare the data payload exactly matching the VBA structure.

    Parameters:
    - ws_start (dict): Dictionary containing 'D3' (FC name) and 'D4' (Date).
    - csrf_token (str): CSRF token string.

    Returns:
    - str: Prepared payload string.
    """
    try:
        dDate = ws_start['D4']
        if not isinstance(dDate, datetime):
            dDate = datetime.strptime(dDate, "%Y-%m-%d %H:%M:%S")

        # Quote the FC name exactly like VBA
        fc = f'"{ws_start["D3"]}"'  # This matches the VBA: fc = """" & wsStart.Range("D3").Value & """"

        # Build data string exactly matching VBA structure
        data_str = 'data={"data":{'
        data_str += f'"view":"Weekly",'
        data_str += f'"ruleOf7":"true",'
        data_str += f'"compStartDate":"{dDate.strftime("%Y")}",'
        data_str += f'"compEndDate":"{iso_week_number(dDate)}",'
        data_str += f'"baseStartDate":"{dDate.strftime("%Y")}",'
        data_str += f'"baseEndDate":"{iso_week_number(dDate)}",'
        data_str += f'"compFc":{fc},'
        data_str += f'"compScenario":"OP2",'
        data_str += f'"baseFc":{fc},'
        data_str += f'"baseScenario":"Labor+Plan+Live+Projection",'
        data_str += f'"comp_benchmark_fc_clusters":[],'
        data_str += f'"base_benchmark_fc_clusters":[],'
        data_str += f'"hours_type":"Hours"'
        data_str += '}}'

        # Build final string exactly like VBA
        final_str = f"csrfmiddlewaretoken={csrf_token}&{data_str}"

        logger.debug(f"Prepared payload: {final_str}")
        return final_str
    except Exception as e:
        logger.error(f"Error preparing data payload: {e}")
        return None
