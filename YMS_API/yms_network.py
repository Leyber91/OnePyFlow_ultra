"""
Network operations for YMS data retrieval using the new direct API with Midway authentication.
Optimized to reduce redundant authentication requests.
"""
import logging
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import os
import re
from datetime import datetime


# Suppress insecure request warnings
urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

def is_html_response(content):
    """
    Check if response content is HTML instead of JSON.
    
    Args:
        content (bytes): Response content to check
        
    Returns:
        bool: True if content appears to be HTML
    """
    # Quick check for HTML tags
    if content.strip().startswith(b'<!DOCTYPE html>') or content.strip().startswith(b'<html'):
        return True
    
    # More thorough check for HTML tags
    # Fixed the invalid escape sequence by using a raw string and proper escape
    html_pattern = re.compile(br'<(?:html|head|body|title|meta|script|link)[>\s]', re.IGNORECASE)
    return bool(html_pattern.search(content))

def get_yms_data_api(site_code, auth=None, max_retries=3, retry_delay=5):
    """
    Retrieve yard management data directly from the new ECFT API endpoint.
    
    Args:
        site_code (str): FC code or external yard code to retrieve data for
        auth (Authentication): Authentication object with Midway session
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Seconds to wait between retries
        
    Returns:
        list: List of yard assets or empty list if retrieval fails
    """
    base_url = "https://ecft.fulfillment.a2z.com/api/ib/get_yms_yard_fc"
    url = f"{base_url}?fc={site_code}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Referer": "https://app.asana.com/",  # Using a generic referrer
    }
    
    # Make sure we have authentication - but don't refresh preemptively
    if auth is None:
        logger.error(f"No authentication provided for {site_code} - API requires Midway authentication")
        return []
    
    # Use the session from Authentication object
    session = auth.session
    
    # Try to get the data with retries
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Requesting YMS data for {site_code} (attempt {attempt}/{max_retries})")
            start_time = time.time()
            
            response = session.get(
                url, 
                headers=headers, 
                timeout=30,
                verify=False  # Skip SSL verification (same as original code)
            )
            
            # Log response time
            elapsed = time.time() - start_time
            logger.info(f"YMS API response time for {site_code}: {elapsed:.2f}s")
            
            # Check if request was successful
            if response.status_code == 200:
                content_length = len(response.content)
                content_type = response.headers.get('Content-Type', '')
                logger.info(f"Response content length: {content_length} bytes, Content-Type: {content_type}")
                
                # Check if we received HTML instead of JSON (authentication redirected to login)
                if 'text/html' in content_type or is_html_response(response.content):
                    logger.error(f"Received HTML instead of JSON for {site_code} - authentication may have failed")
                    if os.environ.get('YMS_DEBUG', '').lower() == 'true':
                        debug_file = f"yms_html_response_{site_code}.html"
                        with open(debug_file, 'wb') as f:
                            f.write(response.content[:2000])  # Save just the beginning
                        logger.info(f"Debug: Saved HTML response beginning to {debug_file}")
                    
                    # Try to refresh authentication and retry - but only if we get HTML (auth failure)

                    # Then replace the authentication retry block:
                    # In yms_network.py
                    if attempt < max_retries:
                        logger.info("Checking authentication for retry...")
                        try:
                            # Check how old the cookie is before deciding to refresh
                            cookie_file_path = auth._get_midway_cookie_path()
                            ctime = os.path.getctime(cookie_file_path)
                            file_age_hours = (datetime.now() - datetime.fromtimestamp(ctime)).total_seconds() / 3600.0
                            
                            # Only force refresh if cookie is older than 1 hour
                            min_age_hours = 1
                            
                            if file_age_hours < min_age_hours:
                                logger.info(f"Cookie is very fresh ({file_age_hours:.2f}h old). Retrying without refresh.")
                                auth._load_cookie()  # Just reload the cookie
                            else:
                                logger.info(f"Cookie is {file_age_hours:.2f}h old. Refreshing authentication...")
                                # Use force_mwinit_reauth directly instead of refresh_cookie_if_needed
                                auth.force_mwinit_reauth(retries=1)
                                auth._load_cookie()
                                
                            logger.info("Retrying in 5 seconds...")
                            time.sleep(5)
                            continue
                        except Exception as e:
                            logger.error(f"Failed during authentication check/refresh: {e}")
                    
                    return []
                
                # Sometimes a 200 response might still have empty content
                if content_length == 0:
                    logger.error(f"Empty response from YMS API for {site_code}")
                    if attempt < max_retries:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    continue
                
                # Try to parse as JSON
                try:
                    data = response.json()
                    record_count = len(data)
                    logger.info(f"Successfully retrieved YMS data for {site_code}: {record_count} records")
                    
                    # If testing, save a copy of the response
                    if os.environ.get('YMS_DEBUG', '').lower() == 'true':
                        import json
                        debug_file = f"yms_response_{site_code}.json"
                        with open(debug_file, 'w') as f:
                            json.dump(data, f, indent=2)
                        logger.info(f"Debug: Saved response to {debug_file}")
                    
                    return data
                except ValueError as e:
                    logger.error(f"Error parsing JSON response for {site_code}: {e}")
                    
                    # If in debug mode, save the raw response
                    if os.environ.get('YMS_DEBUG', '').lower() == 'true':
                        debug_file = f"yms_raw_response_{site_code}.txt"
                        with open(debug_file, 'wb') as f:
                            f.write(response.content)
                        logger.info(f"Debug: Saved raw response to {debug_file}")
            else:
                logger.error(f"YMS API request failed for {site_code} with status code {response.status_code}")
                
            # If we get here, the request failed, so we'll retry
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during YMS API request for {site_code}: {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    # If we've exhausted all retries, return an empty list
    logger.error(f"Failed to retrieve YMS data for {site_code} after {max_retries} attempts")
    return []