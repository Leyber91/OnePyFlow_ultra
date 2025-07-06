# File: data_processing/process_sspot_data.py

import logging
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

def process_sspot_data(retrieval_result):
    """
    Processes the retrieved Shift Schedule (SSPOT) data.
    Ensures correct data types for timestamp columns.

    Parameters:
    - retrieval_result (dict): Dictionary containing the DataFrame and timestamp
                                from pull_sspot_data.

    Returns:
    - pd.DataFrame: Processed DataFrame ready for output, or None if error.
    """
    if not retrieval_result or 'dataframe' not in retrieval_result:
        logger.error("[SSPOT Proc] No valid retrieval result provided.")
        return None

    try:
        df = retrieval_result['dataframe']
        timestamp = retrieval_result['timestamp']
        logger.info(f"[SSPOT Proc] Processing SSPOT data retrieved at {timestamp} ({len(df)} rows).")

        if df.empty:
            logger.warning("[SSPOT Proc] Received empty DataFrame for processing.")
            return df # Return the empty DataFrame

        # --- Data Type Conversion & Validation ---
        timestamp_cols_utc = ['shift_start_timestamp_utc', 'shift_end_timestamp_utc',
                              'break_start_utc', 'break_end_utc']
        timestamp_cols_local = ['shift_start_local', 'shift_end_local',
                                'break_start_local', 'break_end_local']
        date_cols = ['day']
        all_timestamp_cols = timestamp_cols_utc + timestamp_cols_local + date_cols

        for col in all_timestamp_cols:
            if col in df.columns:
                try:
                    # Convert to datetime, coercing errors turns bad data into NaT
                    # Important: Keep as datetime objects for potential later use,
                    # don't convert back to string here unless specifically needed downstream.
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    nat_count = df[col].isna().sum()
                    if nat_count > 0:
                        logger.warning(f"[SSPOT Proc] Column '{col}' has {nat_count} entries that could not be parsed as dates/timestamps.")
                except Exception as dt_err:
                    logger.error(f"[SSPOT Proc] Error converting column '{col}' to datetime: {dt_err}", exc_info=True)
            else:
                 # Only warn if essential columns are missing
                 if col in ['fc', 'shift_start_timestamp_utc', 'shift_end_timestamp_utc', 'shift', 'day', 'shift_start_local', 'shift_end_local']:
                      logger.warning(f"[SSPOT Proc] Expected column '{col}' not found in SSPOT data.")

        # --- Final Processing ---
        # No further processing needed for now, just return the type-corrected DataFrame
        final_df = df

        logger.info("[SSPOT Proc] SSPOT data processing finished.")
        return final_df

    except Exception as e:
        logger.error(f"[SSPOT Proc] Error processing SSPOT data: {e}", exc_info=True)
        return None