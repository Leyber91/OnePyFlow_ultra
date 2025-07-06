"""
Updated Echo module that returns data instead of saving separately.
This module is meant for testing and debugging. It doesn't require Midway authentication.
"""

import os
import json
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def read_config_file():
    """
    Read the configuration file (OnePyFlowParams.json) from the standard location.
    
    Returns:
        dict: The parsed JSON configuration or empty dict if file not found.
    """
    try:
        # Look for the config file in the standard locations
        possible_paths = [
            os.path.expanduser(r"~\Documents\FlexSim 2024 Projects\OnePyFlowParams.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "OnePyFlowParams.json"),
            "OnePyFlowParams.json"
        ]
        
        # Try each possible location
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                    logger.info(f"Configuration loaded from {path}")
                    return config
        
        # If we get here, no config file was found
        logger.warning("No configuration file found in standard locations.")
        return {}
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON configuration: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
        return {}

def EchoFunction():
    """
    A simple debugging function that reads its own configuration and returns timestamp information.
    Returns data instead of saving to file.
    
    Returns:
        dict: Echo diagnostic data or None if error occurs
    """
    try:
        # Read the configuration file
        config = read_config_file()
        
        # Extract parameters
        site = config.get("Site", "UNKNOWN")
        sos_dt = config.get("SOSdatetime", "")
        eos_dt = config.get("EOSdatetime", "")
        plan_type = config.get("plan_type", "UNKNOWN")
        shift = config.get("shift", "UNKNOWN")
        
        # Generate current timestamp
        current_time = datetime.now()
        
        # Format timestamp in multiple ways for debugging
        echo_data = {
            "timestamp_iso": current_time.isoformat(),
            "timestamp_human": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "date": current_time.strftime("%Y-%m-%d"),
            "time": current_time.strftime("%H:%M:%S"),
            "echo_message": "Echo module executed successfully",
            "config": {
                "site": site,
                "sos_datetime": sos_dt,
                "eos_datetime": eos_dt,
                "plan_type": plan_type,
                "shift": shift
            }
        }
        
        logger.info(f"Echo module executed successfully at {echo_data['timestamp_human']}")
        
        # Return the data instead of saving it
        return echo_data
        
    except Exception as e:
        logger.error(f"Error in Echo module: {e}", exc_info=True)
        return None

# When the module is executed directly, run the main function and print result
if __name__ == "__main__":
    result = EchoFunction()
    if result:
        print("Echo data generated successfully!")
        print(json.dumps(result, indent=2))
    else:
        print("Echo function failed")