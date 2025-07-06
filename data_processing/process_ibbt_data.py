#!/usr/bin/env python3
import logging
import pandas as pd
import os

logger = logging.getLogger(__name__)

def process_ibbt_data(csv_path):
    """
    Processes the IBBT CSV data for FlexSim.
    
    Args:
        csv_path (str): Path to the CSV file containing the IBBT data
        
    Returns:
        dict: Dictionary containing IBBT data and metadata
    """
    logger.info(f"[IBBT PROCESS] Processing IBBT data from: {csv_path}")
    
    try:
        # Extract FC from filename before processing the CSV - so we have it even if processing fails
        fc = "UNKNOWN"
        filename = os.path.basename(csv_path)
        
        # Check for the specific pattern in our temp filename: temp_ibbt_FC_timestamp.csv
        if "temp_ibbt_" in filename and "_" in filename:
            # Extract FC from temp_ibbt_FC_timestamp.csv format
            parts = filename.split('_')
            if len(parts) >= 3:
                fc_part = parts[2]  # The FC should be the third part
                # Verify it's actually an FC code (should contain letters and numbers)
                if any(c.isalpha() for c in fc_part) and any(c.isdigit() for c in fc_part):
                    fc = fc_part
        # Also check for direct FC_IBBT.csv format as fallback
        elif "_IBBT" in filename:
            fc_part = filename.split('_IBBT')[0]
            if any(c.isalpha() for c in fc_part) and any(c.isdigit() for c in fc_part):
                fc = fc_part
        
        # Read the CSV file - use the pandas low_memory option to ensure we detect all columns
        df = pd.read_csv(csv_path, low_memory=False)
        logger.info(f"[IBBT PROCESS] Read {len(df)} rows from IBBT CSV with columns: {list(df.columns)}")
        
        # If the DataFrame is empty but has headers, we still want to include structure
        empty_row = None
        column_list = list(df.columns)
        if df.empty and column_list:
            logger.info(f"[IBBT PROCESS] File has headers but no data: {column_list}")
            # Create a placeholder row with the column structure - all empty values
            empty_row = {col: "" for col in column_list}
            # Only numeric columns should be 0 to maintain proper JSON typing
            for col in column_list:
                col_lower = col.lower()
                if any(metric in col_lower for metric in ["vol", "value", "count", "qty", "amount"]):
                    empty_row[col] = 0
                # All other fields including dates should be empty strings
                # We don't set any default values for dates anymore
        
        # Create result dictionary with both data and metadata
        result = {
            "ibbt_data": df.to_dict(orient='records') if not df.empty else ([empty_row] if empty_row else []),
            "metadata": {
                "fc": fc,
                "timestamp": pd.Timestamp.now().isoformat(),
                "row_count": len(df),
                "columns": column_list,
                "filename": os.path.basename(csv_path)
            }
        }
        
        # Delete the temporary CSV file
        try:
            os.remove(csv_path)
            logger.info(f"[IBBT PROCESS] Removed temporary file: {csv_path}")
        except Exception as e:
            logger.warning(f"[IBBT PROCESS] Failed to remove temporary file {csv_path}: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"[IBBT PROCESS] Error processing IBBT data: {e}", exc_info=True)
        
        # Try to delete the temporary file even if processing failed
        try:
            if csv_path and os.path.exists(csv_path):
                os.remove(csv_path)
                logger.info(f"[IBBT PROCESS] Removed temporary file after error: {csv_path}")
        except Exception as rm_error:
            logger.warning(f"[IBBT PROCESS] Failed to remove temporary file: {rm_error}")
            
            # Return empty result with minimum structure and error information
        return {
            "ibbt_data": [
                # Include an empty row with the required columns - all empty values
                {
                    "arc": "",
                    "date": "",
                    "shift": "",
                    "vol": 0  # Only numeric fields should be 0
                }
            ],
            "metadata": {
                "fc": fc,
                "timestamp": pd.Timestamp.now().isoformat(),
                "error": str(e),
                "row_count": 0,
                "columns": ["arc", "date", "shift", "vol"], 
                "filename": os.path.basename(csv_path) if csv_path else "unknown"
            }
        }