# PPR_Each_Receive.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "Each_Receive_function_name": 1,
        "Each_Receive_unit_type": 14,
        "Each_Receive_Size": 15,
        "Each_Receive_Units": 16
    },
    "sums": {
        # Only ReceiveUniversal.INT exists in this dataset - all other functions return 0
        "Each_Receive_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "ReceiveUniversal.INT")],
            "column": 16
        },
        "No_Prep_Req_Prep_Rcv_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "No Prep Req Prep Rcv")],
            "column": 16
        },
        "ReceiveUniversal_BEG_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "ReceiveUniversal.BEG")],
            "column": 16
        },
        "ReceiveUniversal_INT_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "ReceiveUniversal.INT")],
            "column": 16
        },
        "Receive_Small_A_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "Receive Small A")],
            "column": 16
        },
        "Receive_Universal_EXP_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "ReceiveUniversal.EXP")],
            "column": 16
        },
        "Receive_Large_A_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "Receive Large A")],
            "column": 16
        },
        # Size breakdowns - sum all sizes regardless of function (only ReceiveUniversal.INT exists)
        "SmallsTotal": {
            "conditions": [(15, "Small")],
            "column": 16
        },
        # Fixed: Sum only EACH Total rows, exclude Job Total rows
        "Total": {
            "conditions": [(14, "EACH"), (15, "Total")],
            "column": 16
        }
    }
}

def process_PPR_Each_Receive(df: DataFrame,
                             generic_process,
                             PPR_JSON: Dict[str, Any],
                             config: Dict[str, Any]) -> None:
    logging.info("Processing PPR_Each_Receive...")
    
    # DEBUG: Capture all unique values to understand data structure
    if not df.empty:
        logging.info("=== PPR_Each_Receive DEBUG INFO ===")
        
        # Function names (column 1)
        if len(df.columns) > 0:
            unique_functions = df.iloc[:, 0].dropna().unique()
            logging.info(f"[DEBUG] Unique Function Names: {list(unique_functions)}")
        
        # Unit types (column 14)
        if len(df.columns) > 13:
            unique_unit_types = df.iloc[:, 13].dropna().unique()
            logging.info(f"[DEBUG] Unique Unit Types: {list(unique_unit_types)}")
        
        # Sizes (column 15)
        if len(df.columns) > 14:
            unique_sizes = df.iloc[:, 14].dropna().unique()
            logging.info(f"[DEBUG] Unique Sizes: {list(unique_sizes)}")
        
        # Show all rows with Size='Total' to identify missing functions
        if len(df.columns) > 15:
            total_mask = df.iloc[:, 14] == 'Total'
            total_rows = df[total_mask]
            logging.info(f"[DEBUG] Rows with Size='Total': {len(total_rows)}")
            for idx, row in total_rows.iterrows():
                func_name = row.iloc[0]
                units = row.iloc[15]
                logging.info(f"[DEBUG] Total row - Function: '{func_name}', Units: {units}")
            
            total_sum = total_rows.iloc[:, 15].sum() if len(total_rows) > 0 else 0
            logging.info(f"[DEBUG] Sum of all Total units: {total_sum}")
        
        # Sample data rows for verification
        logging.info(f"[DEBUG] Total rows in DataFrame: {len(df)}")
        if len(df) > 0:
            logging.info(f"[DEBUG] Sample row data (first 5 columns): {df.iloc[0, :5].tolist()}")
        
        logging.info("=== END DEBUG INFO ===")
    
    if "PPR_Each_Receive" not in PPR_JSON:
        PPR_JSON["PPR_Each_Receive"] = {}

    generic_process(df, "PPR_Each_Receive", PPR_JSON, config)
    
    # Enhanced output display for PPR Each Receive section
    if "PPR_Each_Receive" in PPR_JSON:
        each_receive_data = PPR_JSON["PPR_Each_Receive"]
        logging.info("=== PPR EACH RECEIVE RESULTS ===")
        logging.info(f"Each_Receive_TotalUnits: {each_receive_data.get('Each_Receive_TotalUnits', 0)}")
        logging.info(f"ReceiveUniversal_INT_TotalUnits: {each_receive_data.get('ReceiveUniversal_INT_TotalUnits', 0)}")
        logging.info(f"SmallsTotal: {each_receive_data.get('SmallsTotal', 0)}")
        logging.info(f"Total: {each_receive_data.get('Total', 0)}")
        logging.info(f"Expected Total should be: 39,110 (sum of Small+Medium+Large)")
        logging.info("=== END PPR EACH RECEIVE RESULTS ===")
    
    logging.info("Finished PPR_Each_Receive.")
