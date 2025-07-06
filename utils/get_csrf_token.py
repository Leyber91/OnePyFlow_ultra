# utils/get_csrf_token.py

import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def get_csrf_token(session, url, headers):
    """
    Retrieve the CSRF token from the specified URL.

    Parameters:
    - session (requests.Session): The current session object.
    - url (str): The URL to retrieve the CSRF token from.
    - headers (dict): Headers to include in the GET request.

    Returns:
    - str or None: The CSRF token if found, else None.
    """
    try:
        logger.debug(f"Retrieving CSRF token from URL: {url}")
        response = session.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()

        # Parse CSRF token from the response using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})

        if token_input:
            token = token_input['value']
            logger.debug(f"CSRF token retrieved: {token}")
            return token
        else:
            logger.error("CSRF token not found in the response.")
            logger.debug(f"Response content: {response.text[:500]}...")  # Log first 500 characters of response
            return None
    except requests.exceptions.SSLError as ssl_err:
        logger.error(f"SSL Error occurred while retrieving CSRF token: {ssl_err}")
        logger.debug("SSL verification failed. Consider using verify=False for internal services.")
        return None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception while retrieving CSRF token: {req_err}")
        return None
    except Exception as err:
        logger.error(f"Unexpected error while retrieving CSRF token: {err}")
        return None
