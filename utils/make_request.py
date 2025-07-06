# utils/make_request.py

import logging
import requests
import time

logger = logging.getLogger(__name__)

def make_request(session, method, url, headers=None, data=None, retries=3):
    """
    Makes an HTTP request with retry logic.

    Parameters:
    - session (requests.Session): Session object to use for the request.
    - method (str): HTTP method ('GET' or 'POST').
    - url (str): URL to send the request to.
    - headers (dict): Headers to include in the request.
    - data (str): Data to include in the request body.
    - retries (int): Number of retries in case of failure.

    Returns:
    - requests.Response: The response object if successful, None otherwise.
    """
    for attempt in range(1, retries + 1):
        try:
            logger.debug(f"Attempt {attempt}: Making {method} request to {url} with data: {data}")
            if method.upper() == 'GET':
                response = session.get(url, headers=headers, timeout=90, verify=False)  # Disabled SSL verification
            elif method.upper() == 'POST':
                response = session.post(url, headers=headers, data=data, timeout=90, verify=False)  # Disabled SSL verification
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None

            logger.debug(f"Received status code: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"Request to {url} succeeded on attempt {attempt}.")
                return response
            elif response.status_code in [400, 401, 403]:
                logger.error(f"Client error {response.status_code}: {response.text}")
                # For client errors, no point retrying
                return None
            else:
                logger.warning(f"Server returned status code {response.status_code}. Retrying...")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception on attempt {attempt}: {e}")

        # Wait before retrying
        logger.debug("Waiting for 2 seconds before retrying...")
        time.sleep(2)

    logger.error(f"Failed to make request to {url} after {retries} attempts.")
    return None
