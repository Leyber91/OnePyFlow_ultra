# utils/send_http_request.py

import logging

logger = logging.getLogger(__name__)

def send_http_request(session, url):
    """
    Sends an HTTP request with the exact configuration from the standalone version.
    """
    try:
        # Set headers for this specific request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        response = session.get(
            url,
            headers=headers,
            verify=False,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            return response
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error in send_http_request: {e}")
        return None
