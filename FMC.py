"""
FMC_module.py

This module provides the FMCfunction, which:
  1) Uses requests and BeautifulSoup to parse all <table> elements from a given FMC URL (based on Site).
  2) Merges the found tables into one DataFrame, preserving all columns.
  3) Optionally cleans the 'Facility Sequence' column by replacing '->' with '_'.
  
The function is intended to be imported by the YMS processing code to supply additional data (such as VR IDs)
that can be used to fill in missing values in YMS records.
"""

import getpass
import os
from http.cookiejar import MozillaCookieJar
import pandas as pd
import warnings
import requests
from bs4 import BeautifulSoup

# Suppress warnings (review before production use)
warnings.filterwarnings('ignore')

def FMCfunction(Site):
    """
    Upgraded FMCfunction:
      1) Uses requests and BeautifulSoup to parse all <table> elements.
      2) Merges all found tables into one DataFrame, ensuring more complete coverage.
      
    Args:
        Site (str): The FMC site code (e.g., "BHX4", "CDG7", etc.).
    
    Returns:
        pd.DataFrame: A DataFrame containing all columns and rows from the merged tables.
                      If an error occurs or no data is found, an empty DataFrame is returned.
    """
    # 1) Hard-coded URLs for FMC data by site
    ##urls = {
    ##    "CDG7": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/waIdy?view=vrs",
    ##    "WRO5": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/spJ2N?view=vrs",
    ##    "LBA4": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/CIJ29?view=vrs",
    ##    "HAJ1": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/I0JMa?view=vrs",
    ##    "DTM2": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/BCK0B?view=vrs",
    ##    "BHX4": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/KQJU9?view=vrs",
    ##    "ZAZ1": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/YEL9m?view=vrs",
    ##    "TRN3": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/LzLMC?view=vrs"
    ##}

    
    urls = {
        "CDG7": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/oI10yV?view=vrs",
        "WRO5": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/0410vi?view=vrs",
        "LBA4": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/1Y10sQ?view=vrs",
        "HAJ1": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/n210sU?view=vrs",
        "DTM1": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/Fk10bB?view=vrs",
        "DTM2": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/fj10mV?view=vrs",
        "BHX4": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/9110zl?view=vrs",
        "ZAZ1": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/sz10iy?view=vrs",
        "TRN3": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/Am10iy?view=vrs"
    }

    ## urls = {
    ##     "CDG7": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/3yXs0?view=vrs",
    ##     "WRO5": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/5bXlq?view=vrs",
    ##     "LBA4": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/M1Xwr?view=vrs",
    ##     "HAJ1": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/hhXDn?view=vrs",
    ##     "DTM2": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/9QXtC?view=vrs",
    ##     "BHX4": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/AFXrt?view=vrs",
    ##     "ZAZ1": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/4GXFb?view=vrs",
    ##     "TRN3": "https://trans-logistics-eu.amazon.com/fmc/excel/execution/yHXqh?view=vrs"
    ## }
    
    url = urls.get(Site)
    if not url:
        # Return an empty DataFrame if the site is unknown
        return pd.DataFrame()
    
    # 2) Load Midway cookie (this is required for authentication)
    user = getpass.getuser()
    cookie_file_path = f'C:/Users/{user}/.midway/cookie'
    if not os.path.exists(cookie_file_path):
        return pd.DataFrame()
    
    cookie_jar = MozillaCookieJar(cookie_file_path)
    try:
        cookie_jar.load()
    except Exception as e:
        return pd.DataFrame()
    
    # 3) Make an HTTP GET request using the loaded cookie
    try:
        response = requests.get(url, cookies=cookie_jar, verify=False)
        if response.status_code != 200:
            return pd.DataFrame()
        # 4) Parse HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all table elements
        tables = soup.find_all("table")
        if not tables:
            return pd.DataFrame()
        
        all_dfs = []
        for table in tables:
            # Extract headers from the table (<th> elements)
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            if not headers:
                # Skip tables without headers
                continue
            
            rows = []
            tr_elements = table.find_all("tr")
            # Assume the first row is headers and process remaining rows
            for tr in tr_elements[1:]:
                td_elems = tr.find_all("td")
                if len(td_elems) == len(headers):
                    row_vals = [td.get_text(strip=True) for td in td_elems]
                    rows.append(row_vals)
            if rows:
                df_part = pd.DataFrame(rows, columns=headers)
                all_dfs.append(df_part)
        
        if not all_dfs:
            return pd.DataFrame()
        
        final_df = pd.concat(all_dfs, ignore_index=True)
        # Optionally, clean the 'Facility Sequence' column
        if 'Facility Sequence' in final_df.columns:
            final_df['Facility Sequence'] = final_df['Facility Sequence'].str.replace('->', '_')
        
        return final_df
    except requests.RequestException as e:
        return pd.DataFrame()
