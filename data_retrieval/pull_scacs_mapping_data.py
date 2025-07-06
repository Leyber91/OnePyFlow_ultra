# File: data_retrieval/pull_scacs_mapping_data.py

import logging
import pandas as pd
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Define the path to the SCACs mapping file
SCACS_FILE_PATH = r'\\ant\dept-eu\BCN1\Public\ECFT\IXD\SCACs Mapping\SCACs_Mapping.txt'

def pull_scacs_mapping_data(fc, start_date, end_date, session, cookie_jar):
    """
    Retrieves SCACs Mapping data from the SCACs_Mapping.txt file
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
        logger.info(f"[SCACs] Attempting to read SCACs Mapping data for FC '{fc}' from: {SCACS_FILE_PATH}")

        # --- 1. Check if file exists ---
        if not os.path.exists(SCACS_FILE_PATH):
            logger.error(f"[SCACs] SCACs Mapping file not found at: {SCACS_FILE_PATH}")
            return None

        # --- 2. Check file size (optional but helpful) ---
        try:
            file_size = os.path.getsize(SCACS_FILE_PATH)
            logger.info(f"[SCACs] Found SCACs Mapping file. Size: {file_size} bytes")
            if file_size < 50:  # Check if file seems too small
                logger.warning(f"[SCACs] SCACs Mapping file size is very small ({file_size} bytes). May be empty or header-only.")
        except Exception as size_err:
            logger.error(f"[SCACs] Could not get file size for {SCACS_FILE_PATH}: {size_err}")

        # --- 3. Read the tab-separated file ---
        try:
            df = pd.read_csv(SCACS_FILE_PATH, sep='\t', on_bad_lines='warn')
            logger.info(f"[SCACs] Successfully read {len(df)} total rows from SCACs_Mapping.txt.")
        except pd.errors.EmptyDataError:
            logger.error(f"[SCACs] SCACs Mapping file is empty or contains no columns: {SCACS_FILE_PATH}")
            return None
        except Exception as read_err:
            logger.error(f"[SCACs] Error reading SCACs Mapping file using pandas: {read_err}", exc_info=True)
            return None

        if df.empty:
            logger.warning("[SCACs] SCACs Mapping file was read but resulted in an empty DataFrame.")

        # --- 4. Verify 'fc' column exists ---
        if 'fc' not in df.columns:
            logger.error(f"[SCACs] 'fc' column not found in SCACs_Mapping.txt. Columns available: {df.columns.tolist()}")
            return None

        # --- 5. Filter by FC ---
        if fc:
            logger.info(f"[SCACs] Filtering SCACs Mapping data for FC: {fc}")
            filtered_df = df[df['fc'].str.upper() == fc.upper()].copy()
            logger.info(f"[SCACs] Filtered down to {len(filtered_df)} rows for FC {fc}.")

            if filtered_df.empty:
                logger.warning(f"[SCACs] No rows found for FC '{fc}' in SCACs_Mapping.txt.")
                # Unlike SSPOT, return an empty dataframe instead of None since FlexSim might need to know there are no mappings
                filtered_df = pd.DataFrame(columns=df.columns)
        else:
            logger.warning("[SCACs] No FC provided to filter SCACs Mapping data. Returning full dataset.")
            filtered_df = df.copy()

        # --- 6. Prepare return data ---
        retrieval_result = {
            'dataframe': filtered_df,
            'timestamp': timestamp
        }

        logger.info(f"[SCACs] SCACs Mapping data retrieval for FC '{fc}' completed successfully with {len(filtered_df)} rows.")
        return retrieval_result

    except FileNotFoundError:
        logger.error(f"[SCACs] SCACs Mapping file not found (FileNotFoundError): {SCACS_FILE_PATH}")
        return None
    except Exception as e:
        logger.error(f"[SCACs] An unexpected error occurred in pull_scacs_mapping_data: {e}", exc_info=True)
        return None