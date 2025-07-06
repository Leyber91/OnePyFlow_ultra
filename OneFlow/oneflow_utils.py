# oneflow_utils.py
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_parameters(site: str, FC_TO_COUNTRY: dict):
    try:
        mp = FC_TO_COUNTRY.get(site, 'Unknown')
        if mp == 'Unknown':
            logger.error(f"Unknown MP for FC '{site}'.")
        today = datetime.today().date()
        days_since_sunday = (today.weekday() + 1) % 7
        last_sunday = today - timedelta(days=days_since_sunday)
        start_date = today if days_since_sunday == 0 else last_sunday
        logger.debug(f"Retrieved parameters: FC={site}, MP={mp}, StartDate={start_date}")
        return {'FC': site, 'MP': mp, 'StartDate': start_date}
    except Exception as e:
        logger.error(f"Error retrieving parameters: {e}", exc_info=True)
        raise

def parse_datetime(dt_str: str):
    possible_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d"
    ]
    for fmt in possible_formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    logger.warning(f"parse_datetime: Could not parse '{dt_str}' with known formats. Using now() as fallback.")
    return datetime.now()

def merge_json_dicts(existing_data, new_data):
    for key, value in new_data.items():
        existing_data[key] = value
    return existing_data

def reorder_modules(data_dict, module_order):
    ordered_result = {}
    for mod in module_order:
        if mod in data_dict:
            ordered_result[mod] = data_dict[mod]
    if "Audit" in data_dict:
        ordered_result["Audit"] = data_dict["Audit"]
    for k, v in data_dict.items():
        if k not in module_order and k != "Audit":
            ordered_result[k] = v
    return ordered_result
