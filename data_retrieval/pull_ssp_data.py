from requests_negotiate_sspi import HttpNegotiateAuth
import requests
import logging
import pandas as pd
from datetime import datetime
from utils.utils import (
    parse_json_response, 
    make_request, 
    process_load_fullness, 
    process_trailer_container_count,
)
import os

from utils.authenticate import Authentication  



# Configure logging
logger = logging.getLogger(__name__)



def pull_ssp_data(fc, start_date, end_date, session, cookie_jar):
    """
    Retrieves SSPPull data for the given FC and date range.

    Parameters:
    - fc (str): Fulfillment Center code.
    - start_date (str): Start date in YYYY-MM-DD format.
    - end_date (str): End date in YYYY-MM-DD format.
    - session (requests.Session): Session object to use for requests.
    - cookie_jar (CookieJar): Cookie jar with authentication cookies.

    Returns:
    - dict: Dictionary containing the final DataFrame and timestamp.
    """
    try:
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Load Midway cookies if not already loaded
        if not cookie_jar:
            cookie_file_path = f'C:/Users/{os.getlogin()}/.midway/cookie'  # Adjust path as needed
            cookie_jar = Authentication().load_midway_cookies(cookie_file_path)
            if not cookie_jar:
                logger.error("Cannot proceed without Midway cookies.")
                return None

        # Initialize session with Midway cookies
        if not session:
            session = requests.Session()
        session.cookies = cookie_jar

        # Initialize Negotiate (SSPI) authentication
        kerberos_auth = HttpNegotiateAuth()
        session.auth = kerberos_auth

        # Define headers (without 'Host')
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://trans-logistics-eu.amazon.com/ssp/dock/hrz/ob",
            "Connection": "keep-alive",
            "Origin": "https://trans-logistics-eu.amazon.com",
        }

        # Initial GET Request to establish session
        url_initial_get = "https://trans-logistics-eu.amazon.com/ssp/dock/hrz/ob"
        logger.info("Making initial GET request to establish session.")
        response_initial = make_request(session, 'GET', url_initial_get, headers=headers)

        if not response_initial:
            logger.error("Failed to establish session with initial GET request.")
            return None

        # First POST Request: Get Default Outbound Dock View
        postdata1 = f"entity=getDefaultOutboundDockView&nodeId={fc}"
        url_fetchdata = "https://trans-logistics-eu.amazon.com/ssp/dock/hrz/ob/fetchdata"
        logger.info("Making first POST request to fetch Default Outbound Dock View data.")
        response1 = make_request(session, 'POST', url_fetchdata, headers=headers, data=postdata1)

        if not response1:
            logger.error("Failed to retrieve Default Outbound Dock View data.")
            return None

        json1 = parse_json_response(response1.text)
        if not json1:
            logger.error("Failed to parse JSON from first POST response.")
            return None

        # Parse first JSON response
        aaData = json1.get("ret", {}).get("aaData", [])
        if not aaData:
            logger.error("No data found in Default Outbound Dock View response.")
            return None

        # Prepare list of dictionaries with selected columns
        data_rows = []
        for item in aaData:
            load = item.get("load", {})
            trailer = item.get("trailer", {})
            row = {
                "vrId": load.get("vrId", ""),
                "route": load.get("route", ""),
                "TrailerID": trailer.get("trailerId", "") if trailer else ""
            }
            data_rows.append(row)

        # Create DataFrame from list of dictionaries
        df = pd.DataFrame(data_rows)

        logger.info(f"Fetched and parsed {len(df)} records from Default Outbound Dock View.")

        # Second POST Request: Get Load Fullness For Loads
        load_ids = ",".join(df['vrId'].astype(str))
        postdata2 = f"entity=getLoadFullnessForLoads&nodeId={fc}&loadIds={load_ids}"
        logger.info("Making second POST request to fetch Load Fullness data.")
        response2 = make_request(session, 'POST', url_fetchdata, headers=headers, data=postdata2)

        if not response2:
            logger.error("Failed to retrieve Load Fullness data.")
            return None

        json2 = parse_json_response(response2.text)
        if not json2:
            logger.error("Failed to parse JSON from second POST response.")
            return None

        # Process Load Fullness Data
        load_fullness = process_load_fullness(json2)
        # Update DataFrame
        df['availableCapacityPercentage'] = df['vrId'].map(load_fullness).fillna("null")

        # Third POST Request: Get Trailer Container Count For Trailer IDs
        trailer_ids = ",".join(df['TrailerID'].astype(str).dropna().unique())
        if trailer_ids:
            postdata3 = f"entity=getTrailerContainerCountForTrailerIds&trailerIds={trailer_ids}&nodeId={fc}"
            logger.info("Making third POST request to fetch Trailer Container Count data.")
            response3 = make_request(session, 'POST', url_fetchdata, headers=headers, data=postdata3)

            if not response3:
                logger.error("Failed to retrieve Trailer Container Count data.")
            else:
                json3 = parse_json_response(response3.text)
                if not json3:
                    logger.error("Failed to parse JSON from third POST response.")
                else:
                    # Process Trailer Container Count Data
                    trailer_counts = process_trailer_container_count(json3)
                    # Add Totes and Cartons to DataFrame
                    df['Totes'] = df['TrailerID'].map(lambda x: trailer_counts.get(x, {}).get("Totes", 0))
                    df['Cartons'] = df['TrailerID'].map(lambda x: trailer_counts.get(x, {}).get("Cartons", 0))
        else:
            logger.warning("No Trailer IDs found to fetch Trailer Container Count data.")
            # Assign default values if no Trailer IDs are found
            df['Totes'] = 0
            df['Cartons'] = 0

        # Select only the required columns
        final_df = df[['vrId', 'route', 'Totes', 'Cartons']].copy()

        # Prepare the return data
        retrieval_result = {
            'dataframe': final_df,
            'timestamp': timestamp
        }

        logger.info("SSPPull data retrieval completed successfully.")
        return retrieval_result

    except Exception as e:
        logger.error(f"An unexpected error occurred in pull_ssp_data: {e}")
        logger.debug("Exception details:", exc_info=True)
        return None
