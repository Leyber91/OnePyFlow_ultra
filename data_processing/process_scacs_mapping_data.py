# File: data_processing/process_scacs_mapping_data.py

import logging
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

def process_scacs_mapping_data(retrieval_result):
    """
    Processes the retrieved SCACs Mapping data.
    Ensures correct data types and formats data for FlexSim.

    Parameters:
    - retrieval_result (dict): Dictionary containing the DataFrame and timestamp
                               from pull_scacs_mapping_data.

    Returns:
    - dict: Processed data dictionary with mappings ready for FlexSim, or None if error.
    """
    if not retrieval_result or 'dataframe' not in retrieval_result:
        logger.error("[SCACs Proc] No valid retrieval result provided.")
        return None

    try:
        df = retrieval_result['dataframe']
        timestamp = retrieval_result['timestamp']
        logger.info(f"[SCACs Proc] Processing SCACs Mapping data retrieved at {timestamp} ({len(df)} rows).")

        if df.empty:
            logger.warning("[SCACs Proc] Received empty DataFrame for processing.")
            # Return an empty but structured result
            return {
                'scacs_mapping': [],
                'metadata': {
                    'timestamp': timestamp,
                    'row_count': 0,
                    'fc_count': 0,
                    'equipment_types': []
                }
            }

        # --- Data Type Conversion & Validation ---
        # Ensure carriercode is string type (some might be empty)
        if 'carriercode' in df.columns:
            df['carriercode'] = df['carriercode'].astype(str)
            # Replace empty or NaN values with empty string for JSON compatibility
            df['carriercode'] = df['carriercode'].replace({'nan': '', 'None': ''})
            
        # --- Format for FlexSim ---
        # Convert to records for JSON serialization
        records = df.to_dict(orient='records')
        
        # Extract metadata
        unique_fcs = df['fc'].unique().tolist()
        unique_equipment_types = df['equipment_type'].unique().tolist() if 'equipment_type' in df.columns else []
        
        # Create final structured output
        result = {
            'scacs_mapping': records,
            'metadata': {
                'timestamp': timestamp,
                'row_count': len(records),
                'fc_count': len(unique_fcs),
                'equipment_types': unique_equipment_types
            }
        }

        logger.info(f"[SCACs Proc] SCACs Mapping data processing finished: {len(records)} records, {len(unique_fcs)} FCs.")
        return result

    except Exception as e:
        logger.error(f"[SCACs Proc] Error processing SCACs Mapping data: {e}", exc_info=True)
        return None