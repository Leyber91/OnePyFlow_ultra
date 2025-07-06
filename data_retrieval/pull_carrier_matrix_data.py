#!/usr/bin/env python3
import logging
import pandas as pd
import io
import requests
import os
import shutil
from datetime import datetime
from io import StringIO
import json
from requests_kerberos import HTTPKerberosAuth, OPTIONAL
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Suppress SSL warnings since we're using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logger = logging.getLogger(__name__)

class CustomS3Client:
    """
    A slimmed-down version of the S3 class specifically for carrier matrix retrieval.
    Does not require TOOLKIT or SETTINGS dependencies.
    """
    def __init__(self, cookie_jar):
        self.cookie_jar = cookie_jar
        self.base = "https://ecft.fulfillment.a2z.com/api/"
        self.bucket = "ecft-json-cache"
        
    def requests_retry_session(self, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504), session=None):
        """
        Create a requests session with retry capabilities, similar to TOOLKIT.connections().
        """
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
        
    def getObject(self, path_to_file):
        """
        Retrieve an object from S3 via the ECFT API.
        
        Args:
            path_to_file (str): Path to the file in S3
            
        Returns:
            str: Text content of the file
        """
        url = f"{self.base}s3/getObject?bucket={self.bucket}&prefix={path_to_file}"
        logger.info(f"[CARRIER_MATRIX S3] Retrieving object from: {url}")
        
        try:
            with self.requests_retry_session() as req:
                resp = req.get(
                    url,
                    cookies=self.cookie_jar,
                    auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL),
                    verify=False,
                    allow_redirects=True,
                    timeout=30
                )
                
            if resp.status_code == 200:
                logger.info(f"[CARRIER_MATRIX S3] Successfully retrieved object (status {resp.status_code})")
                return resp.text
            else:
                logger.warning(f"[CARRIER_MATRIX S3] Failed to retrieve object: status {resp.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[CARRIER_MATRIX S3] Error retrieving object: {e}", exc_info=True)
            return None

def pull_carrier_matrix(fc, midway_session, cookie_jar):
    """
    Retrieves the Carrier Matrix CSV and filters it for the specified FC.
    Uses multiple methods to access the data with fallbacks.
    
    Args:
        fc (str): Fulfillment Center code to filter by (as origin)
        midway_session: Midway session object
        cookie_jar: Cookie jar with authentication cookies
    
    Returns:
        str: Path to a temporary CSV file with filtered carrier matrix data
    """
    logger.info(f"[CARRIER_MATRIX PULL] Starting pull for FC={fc}")
    
    # Timestamp for generating unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_download_path = f"temp_carrier_matrix_download_{timestamp}.csv"
    temp_filtered_path = f"temp_carrier_matrix_{fc}_{timestamp}.csv"
    csv_file_obtained = False
    
    # Method 1: Use custom S3 client implementation based on the provided S3 class
    try:
        logger.info("[CARRIER_MATRIX PULL] Trying CustomS3Client method")
        s3_client = CustomS3Client(cookie_jar)
        carrier_matrix_path = "IXD/Arc_allocation/Carrier_matrix.csv"
        
        csv_content = s3_client.getObject(carrier_matrix_path)
        if csv_content:
            # Write the content to a temporary file
            with open(temp_download_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            logger.info(f"[CARRIER_MATRIX PULL] Successfully downloaded using CustomS3Client: {temp_download_path}")
            csv_file_obtained = True
        else:
            logger.warning("[CARRIER_MATRIX PULL] CustomS3Client returned no content")
    except Exception as e:
        logger.warning(f"[CARRIER_MATRIX PULL] CustomS3Client method failed: {e}")
    
    # Method 2: Try direct API requests if CustomS3Client failed
    if not csv_file_obtained:
        # Define URL endpoints to try in order of preference
        urls_to_try = [
            # 1. Same endpoint used by CustomS3Client but direct approach
            "https://ecft.fulfillment.a2z.com/api/s3/getObject?bucket=ecft-json-cache&prefix=IXD/Arc_allocation/Carrier_matrix.csv",
            
            # 2. Alternative URLs as fallbacks
            "https://diver.qts.amazon.dev/api/download?s3_bucket=ixd-s3-prod&s3_key=IXD/Arc_allocation/Carrier_matrix.csv",
            "https://ecft.fulfillment.a2z.com/api/s3/getObject?bucket=ixd-s3-prod&prefix=IXD/Arc_allocation/Carrier_matrix.csv",
            "https://diver.qts.amazon.dev/api/download?s3_bucket=ixd-s3&s3_key=IXD/Arc_allocation/Carrier_matrix.csv"
        ]
        
        # Try each URL in order
        for url in urls_to_try:
            try:
                logger.info(f"[CARRIER_MATRIX PULL] Trying URL: {url}")
                
                # Use Kerberos authentication if URL is using ecft.fulfillment.a2z.com
                if "ecft.fulfillment.a2z.com" in url:
                    response = requests.get(
                        url,
                        cookies=cookie_jar,
                        auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL),
                        verify=False,
                        allow_redirects=True,
                        timeout=30
                    )
                else:
                    response = requests.get(url, cookies=cookie_jar, verify=False)
                
                response.raise_for_status()  # Raise exception for HTTP errors
                
                # Save the downloaded content
                with open(temp_download_path, 'wb') as f:
                    f.write(response.content)
                    
                logger.info(f"[CARRIER_MATRIX PULL] Successfully downloaded to: {temp_download_path}")
                csv_file_obtained = True
                break
                
            except Exception as e:
                logger.warning(f"[CARRIER_MATRIX PULL] Failed with URL {url}: {e}")
        
    # Method 3: Try network paths if all API methods failed
    if not csv_file_obtained:
        try:
            logger.info("[CARRIER_MATRIX PULL] Trying network paths...")
            network_paths = [
                r"\\ant\dept-eu\BCN1\ECFT\IXD\OnePyFlow\Data\Carrier_matrix.csv",
                r"\\ant\dept-eu\BCN1\Public\ECFT\IXD\OnePyFlow\Data\Carrier_matrix.csv",
                r"\\ant\dept-eu\BCN1\Public\ECFT\IXD\Data\Carrier_matrix.csv",
                r"\\ant\dept-eu\BCN1\Public\ECFT\IXD\OnePyFlow\Outputs\Carrier_matrix.csv"
            ]
            
            for path in network_paths:
                if os.path.exists(path):
                    logger.info(f"[CARRIER_MATRIX PULL] Found file at network path: {path}")
                    shutil.copy2(path, temp_download_path)
                    logger.info(f"[CARRIER_MATRIX PULL] Copied to: {temp_download_path}")
                    csv_file_obtained = True
                    break
        except Exception as e:
            logger.warning(f"[CARRIER_MATRIX PULL] Network path access failed: {e}")
    
    # Method 4: Create a fallback file if all methods failed
    if not csv_file_obtained:
        logger.warning("[CARRIER_MATRIX PULL] All download attempts failed, creating fallback data")
        create_dummy_carrier_matrix(fc, temp_download_path)
    
    # Process the CSV to filter by FC
    try:
        # Load the CSV file
        df = pd.read_csv(temp_download_path)
        logger.info(f"[CARRIER_MATRIX PULL] Loaded CSV with {len(df)} rows")
        
        # Check for required columns and add them if missing
        required_columns = ['origin', 'destination', 'arc_name', 'carrier']
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"[CARRIER_MATRIX PULL] Adding missing column: {col}")
                df[col] = ""
        
        # Filter by origin FC
        filtered_df = df[df['origin'] == fc]
        logger.info(f"[CARRIER_MATRIX PULL] Filtered {len(filtered_df)} rows for FC {fc}")
        
        # If no rows found, create dummy data for this FC
        if filtered_df.empty:
            logger.warning(f"[CARRIER_MATRIX PULL] No data found for FC {fc}, creating dummy data")
            create_dummy_carrier_matrix(fc, temp_filtered_path)
        else:
            # Save filtered data
            filtered_df.to_csv(temp_filtered_path, index=False)
            logger.info(f"[CARRIER_MATRIX PULL] Saved filtered data to: {temp_filtered_path}")
        
        # Clean up the download file
        try:
            os.remove(temp_download_path)
            logger.info(f"[CARRIER_MATRIX PULL] Cleaned up temporary download: {temp_download_path}")
        except Exception as e:
            logger.warning(f"[CARRIER_MATRIX PULL] Failed to remove temporary file: {e}")
        
        return temp_filtered_path
            
    except Exception as e:
        logger.error(f"[CARRIER_MATRIX PULL] Error processing CSV: {e}", exc_info=True)
        
        # Create a fallback file if processing fails
        create_dummy_carrier_matrix(fc, temp_filtered_path)
        return temp_filtered_path

def create_dummy_carrier_matrix(fc, output_path):
    """
    Creates a dummy carrier matrix file with typical destination FCs.
    """
    # Common destination FCs
    typical_destinations = ['MAD4', 'BCN1', 'SVQ1', 'BRU8', 'MXP5', 'MUC3', 'LTN4']
    rows = []
    
    for dest in typical_destinations:
        if dest != fc:  # Don't create a link to itself
            rows.append({
                'origin': fc,
                'destination': dest,
                'arc_name': f'{fc}-{dest}',
                'carrier': 'DEFAULT'
            })
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    logger.info(f"[CARRIER_MATRIX PULL] Created fallback carrier matrix with {len(rows)} rows")
    
    return True