# File: utils/get_graphql_endpoint.py (or appropriate path in your project)

import requests
import logging
import json
# No longer need sys if removing print statements
# import sys

logger = logging.getLogger(__name__)

def get_graphql_endpoint(cookie_string):
    """
    Retrieves the GraphQL endpoint URL from the DockFlow configuration.
    Uses the correct config URL and the correct key ('endpointUrl') from the response JSON.
    """
    logger.info("Retrieving GraphQL endpoint configuration.")
    url = "https://prod-eu.config.dockflow.ops.amazon.dev/"
    logger.debug(f"Target config URL: {url}")

    headers = {
        "Cookie": cookie_string,
        "Origin": "https://prod-eu.dockflow.robotics.a2z.com",
        "Referer": "https://prod-eu.dockflow.robotics.a2z.com/",
        "User-Agent": "Mozilla/5.0"
    }
    logger.debug(f"Request headers (Cookie redacted): {{'Origin': '{headers['Origin']}', 'Referer': '{headers['Referer']}', 'User-Agent': '{headers['User-Agent']}', 'Cookie': 'REDACTED'}}")

    try:
        logger.debug("Making GET request to config URL...")
        response = requests.get(url, headers=headers, verify=False)
        logger.info(f"Config response status: {response.status_code}")
        response.raise_for_status()

        raw_text = None
        try:
            raw_text = response.text
            logger.debug(f"Received RAW config response text (first 500 chars): {raw_text[:500]}...")
        except Exception as e:
            logger.error(f"Could not get raw response text from successful request: {e}")

        logger.debug("Attempting to parse config response as JSON...")
        try:
            config_data = response.json()
            logger.debug("Successfully parsed config response as JSON.")
            logger.debug(f"Received config JSON data structure (via logger): {json.dumps(config_data, indent=2)}")

            # --- Try to extract the endpoint using the CORRECT key ---
            key_to_find = 'endpointUrl' # <<< CORRECT KEY IDENTIFIED FROM DEBUG PRINT

            # Use .get() for safer access, returns None if key doesn't exist
            graphql_endpoint = config_data.get(key_to_find)
            logger.debug(f"Attempting to retrieve value using key '{key_to_find}'...")


            # --- Check if endpoint was found and is a string, then return ---
            if graphql_endpoint and isinstance(graphql_endpoint, str):
                logger.info(f"GraphQL endpoint retrieved from config using key '{key_to_find}': {graphql_endpoint}")
                return graphql_endpoint
            else:
                # Log error indicating the key was incorrect or value was invalid
                logger.error(f"Value for key '{key_to_find}' not found or is not a string in the config JSON response. Data: {config_data}")
                raise ValueError(f"Value for GraphQL endpoint key '{key_to_find}' not found or invalid in config JSON.")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode config response as JSON: {e}. Raw text was: {raw_text[:500] if raw_text else 'N/A'}...")
            raise ValueError(f"Config response was not valid JSON: {e}")
        except Exception as e_inner:
            logger.error(f"Unexpected error processing config JSON: {e_inner}", exc_info=True)
            raise

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error retrieving config from {url}: {e.response.status_code} {e.response.reason}", exc_info=True)
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during GET request to config URL {url}: {e}", exc_info=True)
        raise
    except Exception as e_outer:
        logger.error(f"Unexpected error in get_graphql_endpoint function: {e_outer}", exc_info=True)
        raise