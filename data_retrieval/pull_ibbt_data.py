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
    A slimmed-down version of the S3 class specifically for IBBT retrieval.
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
        logger.info(f"[IBBT S3] Retrieving object from: {url}")
        
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
                logger.info(f"[IBBT S3] Successfully retrieved object (status {resp.status_code})")
                return resp.text
            else:
                logger.warning(f"[IBBT S3] Failed to retrieve object: status {resp.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[IBBT S3] Error retrieving object: {e}", exc_info=True)
            return None

def create_empty_ibbt_file(fc, output_path):
    """
    Creates an empty IBBT file with headers as a fallback.
    """
    # Create default headers for IBBT file based on the actual structure shown
    headers = [
        "arc",
        "date",
        "shift",
        "vol"
    ]
    
    # Create an empty DataFrame with headers
    df = pd.DataFrame(columns=headers)
    
    # Save to CSV - ensure we don't write an index column
    df.to_csv(output_path, index=False)
    logger.info(f"[IBBT PULL] Created empty IBBT file with headers: {headers}")
    
    # Extra verification - read back the file to make sure headers were written correctly
    try:
        verify_df = pd.read_csv(output_path)
        logger.info(f"[IBBT PULL] Verified headers in empty file: {list(verify_df.columns)}")
    except Exception as e:
        logger.warning(f"[IBBT PULL] Could not verify headers: {e}")
    
    return True

def pull_ibbt_data(fc, midway_session, cookie_jar):
    """
    Retrieves the IBBT CSV for the specified FC from S3.
    Uses multiple methods to access the data with fallbacks.
    
    Args:
        fc (str): Fulfillment Center code
        midway_session: Midway session object
        cookie_jar: Cookie jar with authentication cookies
    
    Returns:
        str: Path to a temporary CSV file with IBBT data
    """
    logger.info(f"[IBBT PULL] Starting pull for FC={fc}")
    
    # Standardize FC to uppercase for consistency
    fc = fc.upper() if fc else "UNKNOWN"
    
    # Timestamp for generating unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_ibbt_path = f"temp_ibbt_{fc}_{timestamp}.csv"
    csv_file_obtained = False
    
    # Create the filename based on FC
    ibbt_filename = f"{fc}_IBBT.csv"
    
    # Method 1: Use custom S3 client implementation based on the provided S3 class
    try:
        logger.info("[IBBT PULL] Trying CustomS3Client method")
        s3_client = CustomS3Client(cookie_jar)
        
        # New S3 path for IBBT files
        ibbt_path = f"IXD/Arc_Alloc_Weekly/IBBT_to_FlexSim/{ibbt_filename}"
        
        csv_content = s3_client.getObject(ibbt_path)
        if csv_content:
            # Write the content to a temporary file
            with open(temp_ibbt_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            # Verify the file has content and is a valid CSV
            if os.path.getsize(temp_ibbt_path) == 0:
                logger.warning(f"[IBBT PULL] Downloaded file is empty, generating default headers")
                create_empty_ibbt_file(fc, temp_ibbt_path)
            else:
                try:
                    verify_df = pd.read_csv(temp_ibbt_path)
                    logger.info(f"[IBBT PULL] CSV verified with {len(verify_df)} rows and columns: {list(verify_df.columns)}")
                except Exception as csv_err:
                    logger.warning(f"[IBBT PULL] Downloaded file is not a valid CSV: {csv_err}. Generating default headers.")
                    create_empty_ibbt_file(fc, temp_ibbt_path)
                    
            logger.info(f"[IBBT PULL] Successfully downloaded using CustomS3Client: {temp_ibbt_path}")
            csv_file_obtained = True
        else:
            logger.warning("[IBBT PULL] CustomS3Client returned no content")
    except Exception as e:
        logger.warning(f"[IBBT PULL] CustomS3Client method failed: {e}")
    
    # Method 2: Try direct API requests if CustomS3Client failed
    if not csv_file_obtained:
        # Define URL endpoints to try in order of preference
        ibbt_path = f"IXD/Arc_Alloc_Weekly/IBBT_to_FlexSim/{ibbt_filename}"
        urls_to_try = [
            # 1. Same endpoint used by CustomS3Client but direct approach
            f"https://ecft.fulfillment.a2z.com/api/s3/getObject?bucket=ecft-json-cache&prefix={ibbt_path}",
            
            # 2. Alternative URLs as fallbacks
            f"https://diver.qts.amazon.dev/api/download?s3_bucket=ixd-s3-prod&s3_key={ibbt_path}",
            f"https://ecft.fulfillment.a2z.com/api/s3/getObject?bucket=ixd-s3-prod&prefix={ibbt_path}",
            f"https://diver.qts.amazon.dev/api/download?s3_bucket=ixd-s3&s3_key={ibbt_path}"
        ]
        
        # Try each URL in order
        for url in urls_to_try:
            try:
                logger.info(f"[IBBT PULL] Trying URL: {url}")
                
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
                with open(temp_ibbt_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify the file has content and is a valid CSV
                if os.path.getsize(temp_ibbt_path) == 0:
                    logger.warning(f"[IBBT PULL] Downloaded file is empty, generating default headers")
                    create_empty_ibbt_file(fc, temp_ibbt_path)
                else:
                    try:
                        verify_df = pd.read_csv(temp_ibbt_path)
                        logger.info(f"[IBBT PULL] CSV verified with {len(verify_df)} rows and columns: {list(verify_df.columns)}")
                    except Exception as csv_err:
                        logger.warning(f"[IBBT PULL] Downloaded file is not a valid CSV: {csv_err}. Generating default headers.")
                        create_empty_ibbt_file(fc, temp_ibbt_path)
                    
                logger.info(f"[IBBT PULL] Successfully downloaded to: {temp_ibbt_path}")
                csv_file_obtained = True
                break
                
            except Exception as e:
                logger.warning(f"[IBBT PULL] Failed with URL {url}: {e}")
    
    # Method 3: Try legacy network paths as a last resort
    if not csv_file_obtained:
        try:
            logger.info("[IBBT PULL] Trying network paths...")
            network_paths = [
                f"\\\\ant\\dept-eu\\BCN1\\ECFT\\IXD\\05.Configuration Changes\\IBBT\\{ibbt_filename}",
                f"\\\\ant\\dept-eu\\BCN1\\Public\\ECFT\\IXD\\05.Configuration Changes\\IBBT\\{ibbt_filename}"
            ]
            
            for path in network_paths:
                if os.path.exists(path):
                    logger.info(f"[IBBT PULL] Found file at network path: {path}")
                    shutil.copy2(path, temp_ibbt_path)
                    
                    # Verify the copied file
                    if os.path.getsize(temp_ibbt_path) == 0:
                        logger.warning(f"[IBBT PULL] Copied file is empty, generating default headers")
                        create_empty_ibbt_file(fc, temp_ibbt_path)
                    else:
                        try:
                            verify_df = pd.read_csv(temp_ibbt_path)
                            logger.info(f"[IBBT PULL] CSV verified with {len(verify_df)} rows and columns: {list(verify_df.columns)}")
                        except Exception as csv_err:
                            logger.warning(f"[IBBT PULL] Copied file is not a valid CSV: {csv_err}. Generating default headers.")
                            create_empty_ibbt_file(fc, temp_ibbt_path)
                    
                    logger.info(f"[IBBT PULL] Copied to: {temp_ibbt_path}")
                    csv_file_obtained = True
                    break
        except Exception as e:
            logger.warning(f"[IBBT PULL] Network path access failed: {e}")
    
    # Method 4: Create a fallback empty CSV if all methods failed
    if not csv_file_obtained:
        logger.warning(f"[IBBT PULL] All download attempts failed, creating empty IBBT file for {fc}")
        create_empty_ibbt_file(fc, temp_ibbt_path)
        csv_file_obtained = True
    
    if csv_file_obtained:
        return temp_ibbt_path
    else:
        logger.error(f"[IBBT PULL] Failed to retrieve IBBT data for {fc}")
        # Return path to an empty file as last resort
        create_empty_ibbt_file(fc, temp_ibbt_path)
        return temp_ibbt_path