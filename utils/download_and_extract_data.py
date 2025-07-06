# utils/download_and_extract_data.py

import logging
import pandas as pd
from datetime import datetime
import io

logger = logging.getLogger(__name__)

def download_and_extract_data(session, post_url, headers, data_payload_encoded, fc_name):
    """
    Sends a POST request to the specified URL with the given payload and headers.
    Processes the response and returns a DataFrame in memory.

    Parameters:
    - session (requests.Session): The current session object.
    - post_url (str): The URL to send the POST request to.
    - headers (dict): Headers to include in the POST request.
    - data_payload_encoded (str): The encoded data payload for the POST request.
    - fc_name (str): The Fulfillment Center name.

    Returns:
    - tuple: (bool, pd.DataFrame or None)
      - bool: True if successful, False otherwise.
      - pd.DataFrame or None: The extracted DataFrame if successful, else None.
    """
    try:
        # Set Content-Length header
        headers['Content-Length'] = str(len(data_payload_encoded))

        logger.debug(f"Sending POST request to {post_url}")
        response = session.post(
            post_url,
            headers=headers,
            data=data_payload_encoded,
            timeout=30,
            verify=False
        )
        logger.debug(f"POST request response status: {response.status_code}")

        if response.status_code == 200:
            try:
                # Read Excel data directly from response content in memory
                excel_file = io.BytesIO(response.content)
                df = pd.read_excel(excel_file, engine='openpyxl')

                if df.empty:
                    logger.error("Downloaded Excel file is empty.")
                    return False, None

                logger.info(f"Data extracted from Excel: {df.shape}")

                # Previously, we called extract_calculations here, which produced files.
                # That call has been removed to avoid file generation.

                return True, df

            except Exception as e:
                logger.error(f"Error processing Excel data from response: {e}")
                return False, None

        else:
            logger.error(f"Failed to download data. Status Code: {response.status_code}")
            logger.debug(f"Response content: {response.text[:500]}...")
            return False, None

    except Exception as e:
        logger.error(f"Error during data download and extraction: {e}", exc_info=True)
        return False, None
