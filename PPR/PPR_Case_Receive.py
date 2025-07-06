# PPR_Case_Receive.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "Case_Receive_Paid_Hours": 10,
        "Case_Receive_Unit_Type": 14,
        "Case_Receive_Size": 15,
        "Case_Receive_Units": 16
    },
    "sums": {
        "Cases": {
            "conditions": [(15, "Total"), (14, "Case")],
            "column": 16
        },
        "Hours": {
            "conditions": [(15, "Total"), (14, "EACH")],
            "column": 10
        }
    }
}

def process_PPR_Case_Receive(df: DataFrame,
                             generic_process,
                             PPR_JSON: Dict[str, Any],
                             config: Dict[str, Any]) -> None:
    logging.info("Processing PPR_Case_Receive...")
    # Ensure the dictionary key is present
    PPR_JSON["PPR_Case_Receive"] = {}

    # Use the generic process logic
    generic_process(df, "PPR_Case_Receive", PPR_JSON, config)

    logging.info("Finished PPR_Case_Receive.")
