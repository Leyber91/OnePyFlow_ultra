#!/usr/bin/env python3
import logging
import pandas as pd
import os

logger = logging.getLogger(__name__)

def process_carrier_matrix_data(csv_path):
    """
    Processes the Carrier Matrix CSV data for FlexSim.
    
    Args:
        csv_path (str): Path to the CSV file containing the filtered carrier matrix data
        
    Returns:
        dict: Dictionary containing carrier matrix data and metadata
    """
    logger.info(f"[CARRIER_MATRIX PROCESS] Processing carrier matrix from: {csv_path}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        logger.info(f"[CARRIER_MATRIX PROCESS] Read {len(df)} rows from carrier matrix CSV")
        
        # Extract metadata
        if not df.empty:
            fc = df['origin'].iloc[0]
            destinations_count = df['destination'].nunique()
        else:
            fc = "UNKNOWN"
            destinations_count = 0
        
        # Create result dictionary with both data and metadata
        result = {
            "matrix": df.to_dict(orient='records'),
            "metadata": {
                "fc": fc,
                "timestamp": pd.Timestamp.now().isoformat(),
                "row_count": len(df),
                "destinations_count": destinations_count
            }
        }
        
        # Delete the temporary CSV file
        try:
            os.remove(csv_path)
            logger.info(f"[CARRIER_MATRIX PROCESS] Removed temporary file: {csv_path}")
        except Exception as e:
            logger.warning(f"[CARRIER_MATRIX PROCESS] Failed to remove temporary file {csv_path}: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"[CARRIER_MATRIX PROCESS] Error processing carrier matrix: {e}", exc_info=True)
        
        # Try to delete the temporary file even if processing failed
        try:
            if csv_path and os.path.exists(csv_path):
                os.remove(csv_path)
                logger.info(f"[CARRIER_MATRIX PROCESS] Removed temporary file after error: {csv_path}")
        except Exception as rm_error:
            logger.warning(f"[CARRIER_MATRIX PROCESS] Failed to remove temporary file: {rm_error}")
            
        # Return empty result with error information
        return {
            "matrix": [],
            "metadata": {
                "fc": "UNKNOWN",
                "timestamp": pd.Timestamp.now().isoformat(),
                "error": str(e),
                "row_count": 0,
                "destinations_count": 0
            }
        }