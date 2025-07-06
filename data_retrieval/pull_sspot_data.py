# File: data_retrieval/pull_sspot_data.py

import logging
import pandas as pd
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Define the path to the SSPOT file
SSPOT_FILE_PATH = r'\\ant\dept-eu\BCN1\Public\ECFT\IXD\SSPOT\SSPOT.txt'

def pull_sspot_data(fc, start_date, end_date, session, cookie_jar):
    """
    Retrieves Shift Schedule (SSPOT) data from the SSPOT.txt file
    for the given FC.

    Parameters:
    - fc (str): Fulfillment Center code to filter by.
    - start_date, end_date, session, cookie_jar: Not used for this file-based retrieval,
                                                  kept for compatibility with dispatcher.

    Returns:
    - dict: Dictionary containing the filtered DataFrame and a timestamp,
            or None if an error occurs.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        logger.info(f"[SSPOT] Attempting to read SSPOT data for FC '{fc}' from: {SSPOT_FILE_PATH}")

        # --- 1. Check if file exists ---
        if not os.path.exists(SSPOT_FILE_PATH):
            logger.error(f"[SSPOT] SSPOT data file not found at: {SSPOT_FILE_PATH}")
            return None

        # --- 2. Check file size (optional but helpful) ---
        try:
            file_size = os.path.getsize(SSPOT_FILE_PATH)
            logger.info(f"[SSPOT] Found SSPOT file. Size: {file_size} bytes")
            if file_size < 50: # Check if file seems too small
                 logger.warning(f"[SSPOT] SSPOT file size is very small ({file_size} bytes). May be empty or header-only.")
        except Exception as size_err:
            logger.error(f"[SSPOT] Could not get file size for {SSPOT_FILE_PATH}: {size_err}")

        # --- 3. Read the tab-separated file ---
        try:
            df = pd.read_csv(SSPOT_FILE_PATH, sep='\t', on_bad_lines='warn')
            logger.info(f"[SSPOT] Successfully read {len(df)} total rows from SSPOT.txt.")
        except pd.errors.EmptyDataError:
             logger.error(f"[SSPOT] SSPOT file is empty or contains no columns: {SSPOT_FILE_PATH}")
             return None
        except Exception as read_err:
            logger.error(f"[SSPOT] Error reading SSPOT file using pandas: {read_err}", exc_info=True)
            return None

        if df.empty:
             logger.warning("[SSPOT] SSPOT file was read but resulted in an empty DataFrame.")

        # --- 4. Verify 'fc' column exists ---
        if 'fc' not in df.columns:
            logger.error(f"[SSPOT] 'fc' column not found in SSPOT.txt. Columns available: {df.columns.tolist()}")
            return None

        # --- 5. Filter by FC ---
        if fc:
            logger.info(f"[SSPOT] Filtering SSPOT data for FC: {fc}")
            filtered_df = df[df['fc'].str.upper() == fc.upper()].copy()
            logger.info(f"[SSPOT] Filtered down to {len(filtered_df)} rows for FC {fc}.")

            if filtered_df.empty:
                logger.warning(f"[SSPOT] No rows found for FC '{fc}' in SSPOT.txt.")
                return None # No data for this FC
        else:
            logger.error("[SSPOT] No FC provided to filter SSPOT data. This module requires an FC.")
            return None

        # --- 6. Prepare return data ---
        retrieval_result = {
            'dataframe': filtered_df,
            'timestamp': timestamp
        }

        logger.info(f"[SSPOT] SSPOT data retrieval for FC '{fc}' completed successfully.")
        return retrieval_result

    except FileNotFoundError:
        logger.error(f"[SSPOT] SSPOT data file not found (FileNotFoundError): {SSPOT_FILE_PATH}")
        return None
    except Exception as e:
        logger.error(f"[SSPOT] An unexpected error occurred in pull_sspot_data: {e}", exc_info=True)
        return None