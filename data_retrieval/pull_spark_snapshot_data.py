# File: data_retrieval/pull_spark_snapshot_data.py

import logging
import pandas as pd
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Define the path to the SPARK snapshot file
SPARK_FILE_PATH = r'\\ant\dept-eu\BCN1\Public\ECFT\IXD\SPARK snapshot\SPARK_IXD.txt'

def pull_spark_snapshot_data(fc, start_date, end_date, session, cookie_jar):
    """
    Retrieves SPARK snapshot data from the SPARK_IXD.txt file
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
        logger.info(f"[SPARK] Attempting to read SPARK snapshot data for FC '{fc}' from: {SPARK_FILE_PATH}")

        # --- 1. Check if file exists ---
        if not os.path.exists(SPARK_FILE_PATH):
            logger.error(f"[SPARK] SPARK snapshot file not found at: {SPARK_FILE_PATH}")
            return None

        # --- 2. Check file size (optional but helpful) ---
        try:
            file_size = os.path.getsize(SPARK_FILE_PATH)
            logger.info(f"[SPARK] Found SPARK snapshot file. Size: {file_size} bytes")
            if file_size < 50:  # Check if file seems too small
                logger.warning(f"[SPARK] SPARK snapshot file size is very small ({file_size} bytes). May be empty or header-only.")
        except Exception as size_err:
            logger.error(f"[SPARK] Could not get file size for {SPARK_FILE_PATH}: {size_err}")

        # --- 3. Read the tab-separated file ---
        try:
            df = pd.read_csv(SPARK_FILE_PATH, sep='\t', on_bad_lines='warn')
            logger.info(f"[SPARK] Successfully read {len(df)} total rows from SPARK_IXD.txt.")
        except pd.errors.EmptyDataError:
            logger.error(f"[SPARK] SPARK snapshot file is empty or contains no columns: {SPARK_FILE_PATH}")
            return None
        except Exception as read_err:
            logger.error(f"[SPARK] Error reading SPARK snapshot file using pandas: {read_err}", exc_info=True)
            return None

        if df.empty:
            logger.warning("[SPARK] SPARK snapshot file was read but resulted in an empty DataFrame.")

        # --- 4. Verify 'warehouse' column exists ---
        if 'warehouse' not in df.columns:
            logger.error(f"[SPARK] 'warehouse' column not found in SPARK_IXD.txt. Columns available: {df.columns.tolist()}")
            return None

        # --- 5. Filter by FC (warehouse) ---
        if fc:
            logger.info(f"[SPARK] Filtering SPARK snapshot data for FC: {fc}")
            filtered_df = df[df['warehouse'].str.upper() == fc.upper()].copy()
            logger.info(f"[SPARK] Filtered down to {len(filtered_df)} rows for FC {fc}.")

            if filtered_df.empty:
                logger.warning(f"[SPARK] No rows found for FC '{fc}' in SPARK_IXD.txt.")
                # Return an empty dataframe instead of None since FlexSim might need to know there are no entries
                filtered_df = pd.DataFrame(columns=df.columns)
        else:
            logger.warning("[SPARK] No FC provided to filter SPARK snapshot data. Returning full dataset.")
            filtered_df = df.copy()

        # --- 6. Prepare return data ---
        retrieval_result = {
            'dataframe': filtered_df,
            'timestamp': timestamp
        }

        logger.info(f"[SPARK] SPARK snapshot data retrieval for FC '{fc}' completed successfully with {len(filtered_df)} rows.")
        return retrieval_result

    except FileNotFoundError:
        logger.error(f"[SPARK] SPARK snapshot file not found (FileNotFoundError): {SPARK_FILE_PATH}")
        return None
    except Exception as e:
        logger.error(f"[SPARK] An unexpected error occurred in pull_spark_snapshot_data: {e}", exc_info=True)
        return None
