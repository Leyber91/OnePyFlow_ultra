"""
Updated HCTool module that returns data instead of saving it separately.
This module retrieves headcount data from the ECFT API.
Also includes the raw API response as HCTool_unfiltered.
"""

import os
import json
import requests
import getpass
import logging
from datetime import datetime
from http.cookiejar import MozillaCookieJar
import warnings
warnings.filterwarnings('ignore')

# Setup logger for better debugging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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
                    print(f"HCTool: Configuration loaded from {path}")
                    return config
        
        # If we get here, no config file was found
        logger.warning("No configuration file found in standard locations.")
        print("HCTool: No configuration file found in standard locations.")
        return {}
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON configuration: {e}")
        print(f"HCTool: Error decoding JSON configuration: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
        print(f"HCTool: Error reading configuration file: {e}")
        return {}

def HCtoolPuller():
    """
    Function to pull and process data from the ECFT API.
    Returns the processed data instead of saving to a file.
    Also includes the raw API response data as 'HCTool_unfiltered' in the result.
    Now supports all headcount types including day_one, day_two (day 3-5), and veteran.
    
    Returns:
        list: A list of processed headcount data dictionaries or None if error occurs
    """
    try:
        # Load config file
        config = read_config_file()
        if not config:
            logger.error("Failed to load configuration. Cannot proceed.")
            print("HCTool: Failed to load configuration. Cannot proceed.")
            return None
            
        # Load Midway cookie
        cookie_file_path = f'C:/Users/{getpass.getuser()}/.midway/cookie'
        cookie_jar = MozillaCookieJar(cookie_file_path)
        
        try:
            cookie_jar.load()
            logger.info(f"Loaded cookies from {cookie_file_path}")
        except Exception as e:
            logger.error(f"Error loading Midway cookies: {e}")
            print(f"HCTool: Error loading Midway cookies: {e}")
            return None
    
        # Extract parameters from the loaded JSON
        try:
            Date = datetime.strptime(config['SOSdatetime'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            Site = config.get('Site', 'No definido')
            Shift = config.get('shift', 'No definido')
        except (KeyError, ValueError) as e:
            logger.error(f"Error extracting parameters from config: {e}")
            print(f"HCTool: Error extracting parameters from config: {e}")
            return None
    
        # Print extracted parameters for debugging
        logger.info(f"Parameters: Site={Site}, Date={Date}, Shift={Shift}")
        print(f"HCTool: Parameters: Site={Site}, Date={Date}, Shift={Shift}")
            
        # Define the URL for the API request
        url = f"https://ecft.fulfillment.a2z.com/api/headcount/ixd/actual_data?fc={Site}&date={Date}&shift={Shift}"
        logger.info(f"HCTool: The URL for {Site} is: {url}")
        print(f"HCTool: The URL for {Site} is: {url}")
    
        # Make the HTTP request to the API with the loaded cookies
        response = requests.get(url, cookies=cookie_jar, verify=False)
    
        if response.status_code == 200:
            logger.info(f'HCTool: Request successful')
            print(f'HCTool: Request successful')
            data = response.json()
            
            # Store raw data for unfiltered access
            raw_data = data
    
            # Process the JSON to adapt to the new format
            processed_data = []
    
            # Add header with general information
            update_time = datetime.utcnow().isoformat() + "Z"  # Current time for update
            header = {
                "headcount_date": Date + "T00:00:00.000Z",
                "fc": Site,
                "shift": Shift,
                "update_time": update_time
            }
            processed_data.append(header)
    
            # Check if the 'actualHc' is valid and process it
            if isinstance(data, dict) and 'actualHc' in data:
                actual_data = data['actualHc']
                
                if actual_data:
                    # First, group data by ppr_group, pp, and data_type to collect all HC types
                    grouped_data = {}
                    unique_hc_types = set()  # Track which HC types exist in data
                    
                    for entry in actual_data:
                        if isinstance(entry, dict):  # Check if the entry is a dictionary
                            key = (entry.get("ppr_group", "UNKNOWN_PPR"), 
                                   entry.get("pp", "UNKNOWN_PP"), 
                                   entry.get("data_type", "UNKNOWN_TYPE"))
                            
                            hc_type = entry.get("hc_type")
                            unique_hc_types.add(hc_type)  # Track HC type
                            
                            if key not in grouped_data:
                                grouped_data[key] = {
                                    "ppr_group": entry.get("ppr_group", "UNKNOWN_PPR"), 
                                    "pp": entry.get("pp", "UNKNOWN_PP"), 
                                    "data_type": entry.get("data_type", "UNKNOWN_TYPE"),
                                }
                                # Initialize with 0 for every HC type we encounter
                                for existing_type in unique_hc_types:
                                    grouped_data[key][existing_type] = 0
                            
                            # Add the new HC type if we haven't seen it before
                            if hc_type not in grouped_data[key]:
                                grouped_data[key][hc_type] = 0
                                
                            # Add the value
                            grouped_data[key][hc_type] += entry.get("value", 0)
                    
                    # Transform the grouped data into the required format
                    for key, values in grouped_data.items():
                        entry = {
                            "data_type": values["data_type"],
                            "ppr_group": values["ppr_group"],
                            "pp": values["pp"],
                        }
                        
                        # Create a sorted list of HC types (day_one first, day_two second, etc.)
                        # This ensures consistent ordering
                        sorted_hc_types = sorted(
                            [t for t in values.keys() if t not in ["data_type", "ppr_group", "pp"]]
                        )
                        
                        # Now add each HC type and value with sequential numbering
                        hc_count = 0
                        for hc_type in sorted_hc_types:
                            value = values[hc_type]
                            if value > 0:
                                hc_count += 1
                                entry[f"hc_type_{hc_count}"] = hc_type
                                entry[f"value_{hc_count}"] = value
                        
                        # Only add entries that have at least one HC value
                        if hc_count > 0:
                            processed_data.append(entry)
                else:
                    logger.warning("No actual headcount data found in 'actualHc'.")
                    print("HCTool: No actual headcount data found in 'actualHc'.")
                    
                    # Still include raw data even with empty processed data
                    processed_data.append({"HCTool_unfiltered": raw_data})
                    return processed_data
            else:
                logger.warning(f"Invalid or missing 'actualHc' in the API response.")
                print(f"HCTool: Invalid or missing 'actualHc' in the API response.")
                
                # Include raw data even with error
                processed_data.append({"HCTool_unfiltered": raw_data})
                return processed_data
    
            logger.info(f"HCTool: Successfully processed {len(processed_data) - 1} data records")
            print(f"HCTool: Successfully processed {len(processed_data) - 1} data records")
            
            # Save a local debug copy if needed (but only locally)
            try:
                debug_dir = os.path.expanduser(r"~\Documents\FlexSim 2024 Projects")
                os.makedirs(debug_dir, exist_ok=True)
                debug_file = os.path.join(debug_dir, "HCTool_debug.json")
                
                with open(debug_file, "w") as f:
                    json.dump(processed_data, f, indent=4)
                logger.info(f"Debug copy saved locally to: {debug_file}")
            except Exception as save_err:
                logger.warning(f"Could not save debug copy: {save_err}")
            
            # Add unfiltered data to the processed data
            processed_data.append({"HCTool_unfiltered": raw_data})
            
            # Return the processed data with unfiltered data included
            return processed_data
    
        else:
            logger.error(f"HCTool: Error gathering data: {response.status_code}")
            print(f"HCTool: Error gathering data: {response.status_code}")
            return None
            
    except requests.RequestException as e:
        logger.error(f"HCTool: Error in HTTP request: {e}")
        print(f"HCTool: Error in HTTP request: {e}")
        return None
    except Exception as e:
        logger.error(f"HCTool: Unexpected error: {e}", exc_info=True)
        print(f"HCTool: Unexpected error: {e}")
        return None

# When run directly, execute the function and print the result
if __name__ == "__main__":
    result = HCtoolPuller()
    if result:
        print(f"HCTool execution successful: {len(result) - 1} processed records retrieved")
        print("Raw unfiltered data is also included")
    else:
        print("HCTool execution failed")