# PPR_FF.py

import json
import logging
from datetime import datetime
from typing import Dict, Any, Union

from .PPR_processor import PPRProcessor

def parse_as_datetime(dt_input: Union[str, datetime]) -> datetime:
    """
    If dt_input is already datetime, return it as is.
    If it's a string, attempt to parse it using common formats.
    If parsing fails, fallback to datetime.now().
    """
    if isinstance(dt_input, datetime):
        return dt_input

    possible_formats = [
        "%Y-%m-%d %H:%M:%S",   # e.g. "2025-01-14 18:00:00"
        "%Y-%m-%dT%H:%M:%S",   # e.g. "2025-01-14T18:00:00"
        "%Y-%m-%d"             # fallback if only date
    ]
    for fmt in possible_formats:
        try:
            return datetime.strptime(dt_input, fmt)
        except ValueError:
            pass

    logging.warning(f"parse_as_datetime: Could not parse '{dt_input}' with known formats. Using now() as fallback.")
    return datetime.now()


def PPRfunction(Site: str, SOSdatetime, EOSdatetime) -> Dict[str, Any]:
    """
    Interface function to execute PPR processing.
    Ensures that SOSdatetime and EOSdatetime are real datetime objects 
    before creating PPRProcessor.
    """

    # 1) Convert SOSdatetime / EOSdatetime to datetime if needed
    sos_dt = parse_as_datetime(SOSdatetime)
    eos_dt = parse_as_datetime(EOSdatetime)

    # 2) Now pass them as true datetime objects into PPRProcessor
    processor = PPRProcessor(Site, sos_dt, eos_dt)
    return processor.run()

# Example usage (commented out):
# if __name__ == "__main__":
#     Site = "ZAZ1"
#     # Passing strings or actual datetime objects both work now:
#     result = PPRfunction("ZAZ1", "2025-01-14 06:00:00", "2025-01-14 14:30:00")
#     print(json.dumps(result, indent=4))
