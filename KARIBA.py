"""
KARIBA module that extracts picked WIP data from RODEO.
This module is part of the KARIBA-TSI planning feature for Flexsim.

It retrieves data about already picked units from Kariba that will be
displayed as part of the TSI backlog that needs to be processed.

Supported sites:
- KAR1 → ZAZ1
- KAR3 → TRN3
"""

import logging
import re
from datetime import datetime
import requests
from http.cookiejar import MozillaCookieJar
import getpass
import pandas as pd
import warnings
from bs4 import BeautifulSoup
import io

# Create or retrieve a logger
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

def KARIBAPuller(Site=None):
    """
    Pulls picked WIP data from RODEO for KARIBA-TSI planning.
    
    Args:
        Site (str, optional): The site code (e.g., 'KAR1'). 
                             If None, tries to determine from config.
    
    Returns:
        dict: A dictionary containing KARIBA picked data or None if an error occurs
    """
    logger.info("KARIBA: Starting data extraction")
    
    # If Site is not provided, try to determine it from context
    if not Site:
        try:
            import os
            import json
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
                        Site = config.get("Site", "")
                        logger.info(f"KARIBA: Site '{Site}' loaded from configuration")
                        break
            
            if not Site:
                logger.error("KARIBA: No site provided and could not determine from config")
                return None
        except Exception as e:
            logger.error(f"KARIBA: Error reading configuration: {e}")
            return None
    
    # Determine Kariba site and destination FC
    if 'KAR1' in Site:
        kariba_site = 'KAR1'
        destination_fc = 'ZAZ1'
    elif 'KAR3' in Site:
        kariba_site = 'KAR3'
        destination_fc = 'TRN3'
    elif Site in ['ZAZ1', 'TRN3']:
        # Handle case where FC is provided instead of Kariba site
        if Site == 'ZAZ1':
            kariba_site = 'KAR1'
            destination_fc = 'ZAZ1'
        else:  # TRN3
            kariba_site = 'KAR3'
            destination_fc = 'TRN3'
    else:
        logger.error(f"KARIBA: Unsupported site format: {Site}")
        return None
    
    logger.info(f"KARIBA: Pulling data for {kariba_site} to {destination_fc}")
    
    # 1) Load cookies from Midway
    try:
        cookie_file_path = f'C:/Users/{getpass.getuser()}/.midway/cookie'
        cookie_jar = MozillaCookieJar(cookie_file_path)
        cookie_jar.load()
    except Exception as e:
        logger.error(f"KARIBA: Error loading cookie: {e}")
        return None

    # 2) Build the target URL for PickingPicked WIP
    process_path = f"PPTrans{destination_fc}Case"
    url = f"https://rodeo-dub.amazon.com/{kariba_site}/ItemList?WorkPool=PickingPicked&ProcessPath={process_path}&shipmentType=TRANSSHIPMENTS"
    
    try:
        # 3) Send GET request
        logger.info(f"KARIBA: Requesting data from URL: {url}")
        response = requests.get(url, cookies=cookie_jar, verify=False)
        status_code = response.status_code
        logger.info(f"KARIBA: HTTP status code: {status_code}")

        if status_code != 200:
            logger.warning(f"KARIBA: Error in HTTP request: {status_code}")
            return None

        # 4) Parse the HTML response
        logger.info("KARIBA: Request successful. Parsing HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 5) Find the data table
        data_table = None
        
        # Look for table with headers containing 'quantity'
        for table in soup.find_all('table'):
            headers = [th.get_text().strip().lower() for th in table.find_all('th')]
            if any('quantity' in header for header in headers):
                data_table = table
                logger.info(f"KARIBA: Found table with headers: {headers}")
                break
        
        if not data_table:
            # Fallback to any table with rows
            tables = soup.find_all('table')
            for table in tables:
                if table.find_all('tr'):
                    data_table = table
                    logger.info(f"KARIBA: Using fallback table with {len(table.find_all('tr'))} rows")
                    break
        
        if not data_table:
            logger.error("KARIBA: Could not find data table in response")
            return None
        
        # 6) Extract headers and rows
        headers = [header.get_text().strip() for header in data_table.find_all('th')]
        rows = []
        
        for row in data_table.find_all('tr'):
            cells = row.find_all('td')
            if cells:  # Skip header row
                rows.append([cell.get_text().strip() for cell in cells])
        
        if not rows:
            logger.warning("KARIBA: No data rows found in table")
            return {
                "total_units": 0,
                "units": [],
                "item_count": 0,
                "extraction_time": datetime.now().isoformat(),
                "kariba_site": kariba_site,
                "destination_fc": destination_fc
            }
        
        # 7) Create DataFrame from extracted data
        df = pd.DataFrame(rows, columns=headers if len(headers) == len(rows[0]) else None)
        
        # 8) Find the quantity column
        quantity_column = None
        for col in df.columns:
            if 'quantity' in col.lower():
                quantity_column = col
                logger.info(f"KARIBA: Found quantity column: {col}")
                break
        
        if not quantity_column:
            logger.warning("KARIBA: Could not identify quantity column, trying index-based approach")
            # Try to use column position (often quantity is 10th column)
            if len(df.columns) >= 11:
                quantity_column = df.columns[10]  # 11th column (index 10)
                logger.info(f"KARIBA: Using column at position 10: {quantity_column}")
            elif len(df.columns) > 2:
                # Try any column that can be converted to numeric
                for col in df.columns:
                    try:
                        if pd.to_numeric(df[col], errors='coerce').notna().any():
                            quantity_column = col
                            logger.info(f"KARIBA: Using numeric column: {col}")
                            break
                    except:
                        continue
        
        if not quantity_column:
            logger.error("KARIBA: Failed to find a valid quantity column")
            return None
        
        # 9) Calculate the total units
        try:
            df[quantity_column] = pd.to_numeric(df[quantity_column], errors='coerce')
            total_units = df[quantity_column].sum()
            units_list = df[quantity_column].fillna(0).tolist()
        except Exception as e:
            logger.error(f"KARIBA: Error calculating units: {e}")
            return None
        
        # 10) Return the results
        result = {
            "total_units": int(total_units),
            "units": [int(u) if not pd.isna(u) else 0 for u in units_list],
            "item_count": len(units_list),
            "extraction_time": datetime.now().isoformat(),
            "kariba_site": kariba_site,
            "destination_fc": destination_fc
        }
        
        logger.info(f"KARIBA: Total units picked: {total_units}")
        logger.info('KARIBA: Data extraction finished!')
        
        return result

    except requests.RequestException as req_error:
        logger.error(f"KARIBA: Request error: {req_error}")
        return None
    except Exception as general_error:
        logger.error(f"KARIBA: Error processing data: {general_error}")
        return None


if __name__ == "__main__":
    # Configure direct logging for standalone testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test the function with different sites
    for site in ['KAR1', 'KAR3']:
        print(f"\nTesting KARIBA puller for {site}:")
        result = KARIBAPuller(site)
        
        if result:
            print(f"Success! Extracted {result['total_units']} units from {result['item_count']} items")
            print(f"Kariba site: {result['kariba_site']}, Destination FC: {result['destination_fc']}")
        else:
            print(f"Failed to extract data for {site}")