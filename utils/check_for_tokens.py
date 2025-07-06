# utils/check_for_tokens.py

import logging

logger = logging.getLogger(__name__)

def check_for_tokens(session, response):
    """
    Helper function to check for tokens in various places.

    Parameters:
    - session (requests.Session): The current session object.
    - response (requests.Response): The response object to check.

    Returns:
    - tuple or None: (id_token, refresh_token) if found, else None.
    """
    try:
        logger.info(f"Checking for tokens in response {response.status_code}")

        # Initialize tokens
        id_token = None
        refresh_token = None

        # Check cookies in the session
        for cookie in session.cookies:
            if cookie.name in ['idToken', 'dockflow.idToken', 'id_token']:
                id_token = cookie.value
            elif cookie.name in ['refreshToken', 'dockflow.refreshToken', 'refresh_token']:
                refresh_token = cookie.value

        # Check response headers if tokens not found in cookies
        if not id_token:
            id_token = response.headers.get('X-Id-Token')
        if not refresh_token:
            refresh_token = response.headers.get('X-Refresh-Token')

        # Try to parse response body if it looks like JSON
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                body = response.json()
                if not id_token:
                    id_token = body.get('id_token') or body.get('idToken')
                if not refresh_token:
                    refresh_token = body.get('refresh_token') or body.get('refreshToken')

                # Check for tokens in nested structures
                if 'data' in body:
                    data = body['data']
                    if not id_token:
                        id_token = data.get('id_token') or data.get('idToken')
                    if not refresh_token:
                        refresh_token = data.get('refresh_token') or data.get('refreshToken')
        except Exception as e:
            logger.debug(f"Failed to parse JSON response: {e}")

        if id_token and refresh_token:
            logger.info("Found authentication tokens!")
            return id_token, refresh_token

        # Log what we found for debugging
        logger.debug(f"ID Token found: {bool(id_token)}")
        logger.debug(f"Refresh Token found: {bool(refresh_token)}")

        return None
    except Exception as e:
        logger.error(f"Error in check_for_tokens: {e}")
        return None
