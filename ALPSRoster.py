# ALPSRoster.py
import logging
import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
import re
import urllib3
from http.cookiejar import MozillaCookieJar

logger = logging.getLogger(__name__)

def ALPSRosterFunction(Site, midway_session=None, cookie_jar=None, session=None):
    """
    Retrieves ALPS Roster data for a specific site using Midway authentication.
    
    Parameters:
    Site (str): The site code (e.g., "ZAZ1")
    midway_session (str, optional): Midway session string
    cookie_jar (MozillaCookieJar, optional): Cookie jar containing authentication cookies
    session (requests.Session, optional): Session object for requests
    
    Returns:
    pandas.DataFrame: DataFrame containing the ALPS Roster data, or None if retrieval fails
    """
    logger.info(f"Starting ALPSRosterFunction for Site: {Site}")
    
    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Use the provided session if available, otherwise create a new session
    current_session = session if session else requests.Session()
    
    # Request data from ALPS Roster URL
    url = f"https://alps-eu.amazon.com/roster_uploads/latest?fc={Site}&is_manual=false&scenario=BASE"
    
    try:
        logger.info(f"Sending request to {url}")
        
        # Use the appropriate authentication method
        if cookie_jar:
            response = current_session.get(url, cookies=cookie_jar, verify=False)
        else:
            # Fallback if no cookie_jar provided (should be rare in OneFlow context)
            response = current_session.get(url, verify=False)
        
        if response.status_code == 200:
            logger.info("Successfully retrieved ALPS Roster page")
            
            # Parse the HTML response to find the Roster Upload Id
            soup = BeautifulSoup(response.text, 'html.parser')
            pattern = re.compile(r'<b>Roster Upload Id:</b>\s*(\d+),')
            match = pattern.search(str(soup))
            
            if match:
                roster_upload_id = match.group(1)
                logger.info(f"Found Roster Upload Id: {roster_upload_id}")
                
                # Get the TSV data using the Roster Upload Id
                tsv_url = f"https://alps-eu.amazon.com/roster_uploads/report/employee/{roster_upload_id}.tsv"
                logger.info(f"Requesting TSV data from {tsv_url}")
                
                # Use the same authentication method for the TSV request
                if cookie_jar:
                    tsv_response = current_session.get(tsv_url, cookies=cookie_jar, verify=False)
                else:
                    tsv_response = current_session.get(tsv_url, verify=False)
                
                if tsv_response.status_code == 200:
                    logger.info("Successfully retrieved TSV data")
                    
                    # Read the TSV data into a DataFrame
                    tsv_data = StringIO(tsv_response.text)
                    df = pd.read_csv(tsv_data, sep='\t')
                    
                    logger.info(f"Parsed TSV data into DataFrame with {len(df)} rows")
                    
                    # Create a result dictionary with DataFrame and metadata
                    result = {
                        "RosterData": df,
                        "Metadata": {
                            "RosterUploadId": roster_upload_id,
                            "RowCount": len(df),
                            "Site": Site,
                            "TimeStamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                    
                    return result
                else:
                    logger.error(f"Error retrieving TSV data: {tsv_response.status_code}")
            else:
                logger.error("Roster Upload Id not found in the response")
        else:
            logger.error(f"Error retrieving ALPS Roster data: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Exception in ALPSRosterFunction: {e}", exc_info=True)
    
    return None