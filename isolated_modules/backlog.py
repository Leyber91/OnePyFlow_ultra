"""
Updated Backlog module that returns data instead of saving it separately.
This module reads configuration from OnePyFlowParams.json and returns data for integration.
Also includes the raw API response in BackLog_unfiltered field.
Handles null values by replacing NaN with empty strings.
"""

import os
import json
import logging
import requests
import pandas as pd
import numpy as np
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
        
        # Try each possible location
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                    logger.info(f"Configuration loaded from {path}")
                    print(f"Backlog Puller: Configuration loaded from {path}")
                    return config
        
        # If we get here, no config file was found
        logger.warning("No configuration file found in standard locations.")
        print("Backlog Puller: No configuration file found in standard locations.")
        return {}
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON configuration: {e}")
        print(f"Backlog Puller: Error decoding JSON configuration: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
        print(f"Backlog Puller: Error reading configuration file: {e}")
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

def convert_nan_to_empty_string(data_list):
    """
    Convert NaN values in a list of dictionaries to empty strings.
    
    Args:
        data_list (list): List of dictionaries potentially containing NaN values
        
    Returns:
        list: Same list with NaN values replaced by empty strings
    """
    if not data_list:
        return []
        
    for item in data_list:
        for key, value in item.items():
            if isinstance(value, float) and np.isnan(value):
                item[key] = ""
    
    return data_list

def BackLogPuller():
    """
    Function to retrieve backlog and arrivals data from the ECFT API.
    Now returns the data instead of saving it to file.
    Includes both processed data and raw API response as 'BackLog_unfiltered'.
    Replaces NaN values with empty strings.
    
    Returns:
        dict: Structured backlog data if successful, None otherwise.
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
            print("BackLog Puller: Missing required parameters: Site, SOSdatetime, or shift.")
            return None
        
        # Parse the date from SOSdatetime for API
        try:
            date = datetime.strptime(sos_dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid SOSdatetime format: {sos_dt}")
            print(f"BackLog Puller: Invalid SOSdatetime format: {sos_dt}")
            # Fallback to current date if parsing fails
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Print extracted parameters for debugging
        logger.info(f"Parameters: Site={site}, Date={date}, Shift={shift}")
        print(f"BackLog Puller: Parameters: Site={site}, Date={date}, Shift={shift}")
        
        # Load Midway cookies
        cookie_jar = load_midway_cookies()
        if not cookie_jar:
            logger.error("Failed to load Midway cookies. Cannot proceed.")
            print("BackLog Puller: Failed to load Midway cookies. Cannot proceed.")
            return None
        
        # Define the URL for the API request - FIXED: removed extra space after date
        url = f"https://ecft.fulfillment.a2z.com/api/headcount/ixd/bl_arrivals?fc={site}&date={date}&shift={shift}"
        logger.info(f"BackLog Puller URL: {url}")
        print(f"BackLog Puller: The URL for {site} is: {url}")
        
        # Make the API request
        response = requests.get(url, cookies=cookie_jar, verify=False)
        
        if response.status_code == 200:
            logger.info("BackLog Puller: Request successful")
            print("BackLog Puller: Request successful")
            
            # Parse the JSON response
            data = response.json()
            
            # Store the raw data for unfiltered access
            raw_data = data
            
            # Save the raw JSON for debugging (but only locally)
            output_dir = os.path.expanduser(r"~\Documents\FlexSim 2024 Projects")
            os.makedirs(output_dir, exist_ok=True)
            
            raw_output_file = os.path.join(output_dir, "BackLog_puller_raw.json")
            with open(raw_output_file, "w") as json_file:
                json.dump(data, json_file, indent=4)
            
            logger.info(f"BackLog Puller: Raw data saved locally to {raw_output_file}")
            print(f"BackLog Puller: Raw data saved locally to {raw_output_file}")
            
            # Process the data into different views
            try:
                # 1. Creating ICC-Yard Chart
                icc_yard_data = [entry for entry in data['blResult'] if entry['location'] == 'ICC-Yard']
                icc_yard_df = pd.DataFrame(icc_yard_data)
                
                # Create a pivot table for ICC-Yard
                icc_yard_pivot = pd.DataFrame()
                if not icc_yard_df.empty:
                    icc_yard_pivot = icc_yard_df.pivot_table(
                        index='group_type',
                        columns='asset_type',
                        values='value',
                        fill_value=0
                    ).reindex(['Parcel Trailers', 'Swap Bodies Trailers', 'Ocean Trailers', 'Double Deck Trailers', 'Other Trailers'])
                    
                    # Ensure the columns are in the right order
                    column_order = ['empty_trailers', 'palletized_trailers', 'fluid_trailers']
                    available_columns = [col for col in column_order if col in icc_yard_pivot.columns]
                    icc_yard_pivot = icc_yard_pivot[available_columns]
                    
                    # Rename columns to readable format
                    column_map = {
                        'empty_trailers': 'Empty Trailers',
                        'palletized_trailers': 'Palletized Trailers',
                        'fluid_trailers': 'Fluid Trailers'
                    }
                    icc_yard_pivot.columns = [column_map.get(col, col) for col in icc_yard_pivot.columns]
                
                # 2. Creating Palletized - Extra chart
                palletized_extra_data = [entry for entry in data['blResult'] if entry['location'] == 'Palletized - Extra']
                palletized_extra_df = pd.DataFrame(palletized_extra_data)
                
                # Create a pivot table for Palletized - Extra
                palletized_extra_pivot = pd.DataFrame()
                if not palletized_extra_df.empty:
                    palletized_extra_pivot = palletized_extra_df.pivot_table(
                        index='group_type',
                        columns='asset_type',
                        values='value',
                        fill_value=0
                    ).reindex([
                        'Not Manifested PAX Pallets', 
                        'Rework Pallets', 
                        'Received Prep Pallets', 
                        'HRV Pallets', 
                        'Hazmat Pallets', 
                        'Other Pallets'
                    ])
                    
                    # Ensure the columns are in the right order
                    column_order = ['dock', 'rest_building']
                    available_columns = [col for col in column_order if col in palletized_extra_pivot.columns]
                    palletized_extra_pivot = palletized_extra_pivot[available_columns]
                    
                    # Rename columns
                    palletized_extra_pivot.columns = ['Dock', 'Rest of the Building']
                
                # 3. Creating Palletized Chart
                palletized_data = [entry for entry in data['blResult'] if entry['location'] == 'Palletized']
                palletized_df = pd.DataFrame(palletized_data)
                
                # Create a pivot table for Palletized
                palletized_pivot = pd.DataFrame()
                if not palletized_df.empty:
                    palletized_pivot = palletized_df.pivot_table(
                        index='group_type',
                        columns='asset_type',
                        values='value',
                        fill_value=0
                    ).reindex([
                        'Decant Pallets',
                        'DICE Pallets',
                        'Docksort/Receive Pallets',
                        'Manual Sort Pallets',
                        'Multi Asin Pallets',
                        'NPC Pallets',
                        'PAX/MonoAsin Pallets',
                        'Prep Pallets',
                        'TSO Pallets',
                        'UIS Pallets'
                    ])
                    
                    # Ensure the columns are in the right order
                    column_order = ['dock', 'rest_building']
                    available_columns = [col for col in column_order if col in palletized_pivot.columns]
                    palletized_pivot = palletized_pivot[available_columns]
                    
                    # Rename columns
                    palletized_pivot.columns = ['Dock', 'Rest of the Building']
                
                # 4. Creating Inventory Chart
                inventory_data = [entry for entry in data['blResult'] if entry['location'] == 'Inventory']
                inventory_df = pd.DataFrame(inventory_data)
                
                # Create a pivot table for Inventory
                inventory_pivot = pd.DataFrame()
                if not inventory_df.empty:
                    inventory_pivot = inventory_df.pivot_table(
                        index='group_type',
                        columns='asset_type',
                        values='value',
                        fill_value=0
                    ).reindex([
                        'Empty AMPAL',
                        'Empty Black Totes Pallets',
                        'Empty EPAL',
                        'Empty R-EPAL'
                    ])
                    
                    # Rename columns
                    inventory_pivot.columns = ['Assets']
                
                # 5. Creating Asset Chart for arrivals
                asset_data = data['arrivalsResult']
                asset_df = pd.DataFrame(asset_data)
                
                # Create a pivot table for Asset arrivals
                asset_pivot = pd.DataFrame()
                if not asset_df.empty:
                    # Ensure required columns exist
                    if all(col in asset_df.columns for col in ['location', 'group_type', 'shift']):
                        asset_pivot = asset_df.pivot_table(
                            index=['location', 'group_type'],
                            columns='shift',
                            values='value',
                            fill_value=0
                        )
                        
                        # Reindex to ensure consistent row order
                        expected_indices = [
                            ('Parcel Trailers', 'Live'),
                            ('Parcel Trailers', 'Drop'),
                            ('Parcel Swap Bodies', 'Live'),
                            ('Parcel Swap Bodies', 'Drop'),
                            ('Parcel Double Deck', 'Live'),
                            ('Parcel Double Deck', 'Drop')
                        ]
                        available_indices = [idx for idx in expected_indices if idx in asset_pivot.index]
                        asset_pivot = asset_pivot.reindex(available_indices)
                        
                        # Rename columns with shift names
                        expected_columns = ['ES', 'LS', 'NS']
                        available_columns = [col for col in expected_columns if col in asset_pivot.columns]
                        asset_pivot.columns = [f"{col} Arrivals" for col in available_columns]
                        
                        # Rename index for better readability
                        asset_pivot.index = [
                            f"{location} - {group_type}" for location, group_type in asset_pivot.index
                        ]
                
                # Convert dataframes to records, replacing NaN with empty strings
                # For icc_yard_pivot
                icc_yard_records = []
                if not icc_yard_pivot.empty:
                    icc_yard_records = icc_yard_pivot.reset_index().replace({np.nan: ""}).to_dict(orient='records')
                
                # For palletized_extra_pivot
                palletized_extra_records = []
                if not palletized_extra_pivot.empty:
                    palletized_extra_records = palletized_extra_pivot.reset_index().replace({np.nan: ""}).to_dict(orient='records')
                
                # For palletized_pivot
                palletized_records = []
                if not palletized_pivot.empty:
                    palletized_records = palletized_pivot.reset_index().replace({np.nan: ""}).to_dict(orient='records')
                
                # For inventory_pivot
                inventory_records = []
                if not inventory_pivot.empty:
                    inventory_records = inventory_pivot.reset_index().replace({np.nan: ""}).to_dict(orient='records')
                
                # For asset_pivot
                asset_records = []
                if not asset_pivot.empty:
                    # Handle multi-index conversion properly
                    asset_pivot = asset_pivot.reset_index()
                    asset_records = asset_pivot.replace({np.nan: ""}).to_dict(orient='records')
                    
                    # Fix column naming for multi-index
                    if 'location' in asset_records[0] and 'group_type' in asset_records[0]:
                        for record in asset_records:
                            record['asset_type'] = f"{record.pop('location')} - {record.pop('group_type')}"
                
                # Combining all the pivot tables into a single dictionary with both processed and raw data
                all_data = {
                    "ICC-Yard": icc_yard_records,
                    "Palletized-Extra": palletized_extra_records,
                    "Palletized": palletized_records,
                    "Inventory": inventory_records,
                    "Asset": asset_records,
                    "Metadata": {
                        "fc": site,
                        "date": date,
                        "shift": shift,
                        "timestamp": datetime.now().isoformat()
                    },
                    "BackLog_unfiltered": raw_data  # Include the raw API response data
                }
                
                logger.info("BackLog Puller: Data processing completed successfully")
                print("BackLog Puller: Data processing completed successfully")
                
                # Return the processed data
                return all_data
                
            except Exception as processing_error:
                logger.error(f"Error processing BackLog data: {processing_error}", exc_info=True)
                print(f"BackLog Puller: Error processing data: {processing_error}")
                # Still return the raw data even if processing failed
                return {
                    "ICC-Yard": [],
                    "Palletized-Extra": [],
                    "Palletized": [],
                    "Inventory": [],
                    "Asset": [],
                    "Metadata": {
                        "fc": site,
                        "date": date,
                        "shift": shift,
                        "timestamp": datetime.now().isoformat(),
                        "error": str(processing_error)
                    },
                    "BackLog_unfiltered": raw_data
                }
        else:
            logger.error(f"BackLog Puller: Error gathering data: HTTP status code {response.status_code}")
            print(f"BackLog Puller: Error gathering data: HTTP status code {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Unexpected error in BackLogPuller: {e}", exc_info=True)
        print(f"BackLog Puller: Unexpected error: {e}")
        return None

# When the module is executed directly, run the function and print the result
if __name__ == "__main__":
    try:
        result = BackLogPuller()
        if result:
            print("BackLog data retrieved successfully!")
            print(f"Data contains {sum(len(v) for k, v in result.items() if k != 'Metadata' and k != 'BackLog_unfiltered')} records across {len(result) - 2} categories")
            print(f"Raw unfiltered data is also included")
        else:
            print("BackLog Puller execution failed")
    except Exception as e:
        print(f"BackLog Puller critical error: {e}")
        logger.critical(f"Critical error in BackLog Puller: {e}", exc_info=True)