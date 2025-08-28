# PPR_PRU.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "PRU_LineItem_Name": 3,
        # Align with processPathRollup schema: cols 7,8,9 = Units, Hours, UPH
        "PRU_Actual_Volume": 7,
        "PRU_Actual_Hours": 8,
        "PRU_Actual_Rate": 9
    },
    "sums": {
        "PrepRecorder_Volume": {"condition": (3, "Prep Recorder - Total"), "column": 7},
        "PrepRecorder_Hours": {"condition": (3, "Prep Recorder - Total"), "column": 8},
        "Cubi_Rate": {"condition": (3, "Cubiscan"), "column": 9},
        "PRU_Receive_Dock": {"condition": (3, "Receive Dock"), "column": 9},
        "PRU_Receive_Support": {"condition": (3, "Receive Support"), "column": 9},
        "PRU_Prep_Support": {"condition": (3, "Prep Support"), "column": 9},
        "PRU_RSR_Support": {"condition": (3, "RSR Support"), "column": 9},
        "PRU_IB_Lead_PA": {"condition": (3, "IB Lead/PA"), "column": 9},
        "PRU_IB_ProblemSolve": {"condition": (3, "IB Problem Solve"), "column": 9},
        "PRU_Transfer_Out_Dock": {"condition": (3, "Transfer Out Dock"), "column": 9},
        "PRU_TO_Lead_PA": {"condition": (3, "TO Lead/PA"), "column": 9},
        "PRU_TO_ProblemSolve": {"condition": (3, "TO Problem Solve"), "column": 9},
        "PRU_Each_Receive_Total": {"condition": (3, "Each Receive - Total"), "column": 9},
        "PRU_LP_Receive": {"condition": (3, "LP Receive"), "column": 9},
        "PRU_RC_Sort_Total": {"condition": (3, "RC Sort - Total"), "column": 9},
        "PRU_Transfer_Out": {"condition": (3, "Transfer Out"), "column": 9}
    }
}

def process_PPR_PRU(df: DataFrame,
                    generic_process,
                    PPR_JSON: Dict[str, Any],
                    config: Dict[str, Any]) -> None:
    """
    Custom method for PPR_PRU. 
    Calls generic_process with this config, then can do extra steps if needed.
    """
    logging.info("Processing PPR_PRU...")
    if "PPR_PRU" not in PPR_JSON:
        PPR_JSON["PPR_PRU"] = {}

    generic_process(df, "PPR_PRU", PPR_JSON, config)

    # Additional custom logic if needed...
    logging.info("Finished PPR_PRU.")
