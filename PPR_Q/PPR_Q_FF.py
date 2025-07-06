import json
import logging
from datetime import datetime
from typing import Dict, Any, Union

try:
    # Try relative import first (when called as package)
    from .PPR_Q_processor import PPRQProcessor
except ImportError:
    # Fall back to absolute import (when called directly)
    from PPR_Q_processor import PPRQProcessor

def parse_as_datetime(dt_input: Union[str, datetime]) -> datetime:
    """
    If dt_input is already datetime, return it as is.
    If it's a string, attempt to parse it using common formats including hour/minute.
    If parsing fails, fallback to datetime.now().
    """
    if isinstance(dt_input, datetime):
        return dt_input

    possible_formats = [
        "%Y-%m-%d %H:%M:%S",   # e.g. "2025-01-14 18:00:00"
        "%Y-%m-%dT%H:%M:%S",   # e.g. "2025-01-14T18:00:00"
        "%Y-%m-%d %H:%M",      # e.g. "2025-01-14 18:00"
        "%Y-%m-%dT%H:%M",      # e.g. "2025-01-14T18:00"
        "%Y-%m-%d"             # fallback if only date
    ]
    for fmt in possible_formats:
        try:
            return datetime.strptime(dt_input, fmt)
        except ValueError:
            pass

    logging.warning(f"parse_as_datetime: Could not parse '{dt_input}' with known formats. Using now() as fallback.")
    return datetime.now()

def PPR_Q_function(Site: str, start_datetime, end_datetime) -> Dict[str, Any]:
    """
    Interface function to execute PPR_Q processing with minute-level granularity.
    Ensures that start_datetime and end_datetime are real datetime objects 
    before creating PPRQProcessor.
    
    Args:
        Site (str): The warehouse site identifier.
        start_datetime: Start datetime (string or datetime object) with minute precision.
        end_datetime: End datetime (string or datetime object) with minute precision.
    
    Returns:
        Dict[str, Any]: Processed PPR_Q data with all metrics.
    """

    # 1) Convert start_datetime / end_datetime to datetime if needed
    start_dt = parse_as_datetime(start_datetime)
    end_dt = parse_as_datetime(end_datetime)

    # 2) Now pass them as true datetime objects into PPRQProcessor
    processor = PPRQProcessor(Site, start_dt, end_dt)
    return processor.run()

# Example usage (commented out):
# if __name__ == "__main__":
#     Site = "DTM2"
#     # Passing strings with minute precision:
#     result = PPR_Q_function("DTM2", "2025-06-13 06:15:00", "2025-06-13 15:00:00")
#     print(json.dumps(result, indent=4)) 