# File: data_processing/process_spark_snapshot_data.py

import logging
import pandas as pd
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def process_spark_snapshot_data(retrieval_result):
    """
    Processes the retrieved SPARK snapshot data.
    Ensures correct data types and formats data for FlexSim.

    Parameters:
    - retrieval_result (dict): Dictionary containing the DataFrame and timestamp
                               from pull_spark_snapshot_data.

    Returns:
    - dict: Processed data dictionary with SPARK data ready for FlexSim, or None if error.
    """
    if not retrieval_result or 'dataframe' not in retrieval_result:
        logger.error("[SPARK Proc] No valid retrieval result provided.")
        return None

    try:
        df = retrieval_result['dataframe']
        timestamp = retrieval_result['timestamp']
        logger.info(f"[SPARK Proc] Processing SPARK snapshot data retrieved at {timestamp} ({len(df)} rows).")

        if df.empty:
            logger.warning("[SPARK Proc] Received empty DataFrame for processing.")
            # Return an empty but structured result
            return {
                'spark_snapshot': [],
                'metadata': {
                    'timestamp': timestamp,
                    'row_count': 0,
                    'warehouse_count': 0,
                    'carriers': [],
                    'origin_fcs': []
                }
            }

        # --- Data Type Conversion & Validation ---
        # Ensure string columns are properly formatted
        string_columns = ['warehouse', 'vrid', 'fmccarrier', 'fmcsubcarrier', 'fmcoriginfc']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
                # Replace empty or NaN values with empty string for JSON compatibility
                df[col] = df[col].replace({'nan': '', 'None': '', 'NaN': ''})

        # Handle datetime columns
        datetime_columns = ['stowbydateutc', 'spark_arrival_fcst_utc']
        for col in datetime_columns:
            if col in df.columns:
                # Convert to string to ensure JSON serialization
                df[col] = df[col].astype(str)
                df[col] = df[col].replace({'nan': '', 'None': '', 'NaN': '', 'nat': ''})

        # Handle numeric columns
        numeric_columns = [
            'spark_spark_ecft_volume', 'units_in_cases', 'cases_total', 
            'units_in_totes', 'totes_total', 'units_in_pallets', 'pallets_total',
            'units_in_pallets_pax', 'pallets_pax_total', 'units_in_cases_pallet',
            'cases_pallet_total', 'units_in_cases_pallet_pax', 'cases_pallet_pax_total',
            'units_in_totes_pallet', 'totes_pallet_total'
        ]
        for col in numeric_columns:
            if col in df.columns:
                # Convert to numeric, replacing NaN with 0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # --- Format for FlexSim ---
        # Convert to records for JSON serialization
        records = df.to_dict(orient='records')
        
        # Extract metadata
        unique_warehouses = df['warehouse'].unique().tolist() if 'warehouse' in df.columns else []
        unique_carriers = df['fmccarrier'].unique().tolist() if 'fmccarrier' in df.columns else []
        unique_origin_fcs = df['fmcoriginfc'].unique().tolist() if 'fmcoriginfc' in df.columns else []
        
        # Create final structured output
        result = {
            'spark_snapshot': records,
            'metadata': {
                'timestamp': timestamp,
                'row_count': len(records),
                'warehouse_count': len(unique_warehouses),
                'carriers': unique_carriers,
                'origin_fcs': unique_origin_fcs
            }
        }

        logger.info(f"[SPARK Proc] SPARK snapshot data processing finished: {len(records)} records, {len(unique_warehouses)} warehouses.")
        return result

    except Exception as e:
        logger.error(f"[SPARK Proc] Error processing SPARK snapshot data: {e}", exc_info=True)
        return None
