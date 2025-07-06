"""
Updated PHC (Predicted Headcount) module that returns only the unfiltered data.
This module retrieves predicted headcount data from the ECFT API and
returns the raw API response as PHC_unfiltered.
"""

import os
import json
import logging
import requests
import pandas as pd
from datetime import datetime
from http.cookiejar import MozillaCookieJar
import getpass
import warnings
warnings.filterwarnings('ignore')

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
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                    logger.info(f"Configuration loaded from {path}")
                    print(f"PHC Puller: Configuration loaded from {path}")
                    return config
        
        logger.warning("No configuration file found in standard locations.")
        print("PHC Puller: No configuration file found in standard locations.")
        return {}
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON configuration: {e}")
        print(f"PHC Puller: Error decoding JSON configuration: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
        print(f"PHC Puller: Error reading configuration file: {e}")
        return {}

def load_midway_cookies():
    """
    Load Midway cookies from the standard cookie file.
    
    Returns:
        MozillaCookieJar: The loaded cookie jar, or None if loading fails.
    """
    try:
        cookie_file_path = f'C:/Users/{getpass.getuser()}/.midway/cookie'
        cookie_jar = MozillaCookieJar(cookie_file_path)
        cookie_jar.load()
        logger.info(f"Loaded cookies from {cookie_file_path}")
        return cookie_jar
    except Exception as e:
        logger.error(f"Error loading Midway cookies: {e}")
        return None

def PHCpuller():
    """
    Function to retrieve predicted headcount data from the ECFT API.
    Returns only the raw API response (unfiltered data).
    """
    try:
        # Read the configuration file
        config = read_config_file()
        if not config:
            logger.error("Failed to load configuration. Cannot proceed.")
            return None
        
        # Extract parameters
        site = config.get("Site", "")
        sos_dt = config.get("SOSdatetime", "")
        shift = config.get("shift", "")
        
        if not site or not sos_dt or not shift:
            logger.error("Missing required parameters: Site, SOSdatetime, or shift.")
            print("PHC Puller: Missing required parameters: Site, SOSdatetime, or shift.")
            return None
        
        # Parse the date from SOSdatetime
        try:
            date = datetime.strptime(sos_dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid SOSdatetime format: {sos_dt}")
            print(f"PHC Puller: Invalid SOSdatetime format: {sos_dt}")
            # Fallback to current date if parsing fails
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Debug info
        logger.info(f"Parameters: Site={site}, Date={date}, Shift={shift}")
        print(f"PHC Puller: Parameters: Site={site}, Date={date}, Shift={shift}")
        
        # Load Midway cookies
        cookie_jar = load_midway_cookies()
        if not cookie_jar:
            logger.error("Failed to load Midway cookies. Cannot proceed.")
            print("PHC Puller: Failed to load Midway cookies. Cannot proceed.")
            return None
        
        # Define the URL for the API request
        # NOTE: Removed the '%20' from date to avoid potential issues
        url = f"https://ecft.fulfillment.a2z.com/api/headcount/ixd/predicted_data?fc={site}&date={date}&shift={shift}"
        logger.info(f"PHC Puller URL: {url}")
        print(f"PHC Puller: The URL for {site} is: {url}")
        
        # Make the API request
        response = requests.get(url, cookies=cookie_jar, verify=False)
        
        if response.status_code == 200:
            logger.info("PHC Puller: Request successful")
            print("PHC Puller: Request successful")
            
            # Parse the JSON response
            raw_data = response.json()
            
            # Save the raw JSON for debugging (but only locally)
            output_dir = os.path.expanduser(r"~\Documents\FlexSim 2024 Projects")
            os.makedirs(output_dir, exist_ok=True)
            raw_output_file = os.path.join(output_dir, "PHC_puller_raw.json")
            
            with open(raw_output_file, "w", encoding="utf-8") as json_file:
                json.dump(raw_data, json_file, indent=4)
            
            logger.info(f"PHC Puller: Raw data saved locally to {raw_output_file}")
            print(f"PHC Puller: Raw data saved locally to {raw_output_file}")
            
            # Return ONLY the unfiltered data
            return raw_data
        
        else:
            logger.error(f"PHC Puller: Error gathering data: HTTP status code {response.status_code}")
            print(f"PHC Puller: Error gathering data: HTTP status code {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Unexpected error in PHCpuller: {e}", exc_info=True)
        print(f"PHC Puller: Unexpected error: {e}")
        return None

if __name__ == "__main__":
    try:
        result = PHCpuller()
        if result is not None:
            print("PHC Puller execution successful. Raw unfiltered data returned.")
            print(result)  # Print or handle raw data as needed
        else:
            print("PHC Puller execution failed.")
    except Exception as e:
        print(f"PHC Puller critical error: {e}")
        logger.critical(f"Critical error in PHC Puller: {e}", exc_info=True)
