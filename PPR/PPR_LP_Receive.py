# PPR_LP_Receive.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "LP_Receive_function_name": 1,
        "LP_Receive_paid_hours_total": 10,
        "LP_Receive_unit_type": 14,
        "LP_Receive_Size": 15,
        "LP_Receive_Units": 16
    },
    "sums": {
        "PID_Receive_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "PID Receive")],
            "column": 16
        },
        "PrEditor_Receive_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "PrEditor Receive")],
            "column": 16
        },
        "PrEditor_Receive_TotalHours": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "PrEditor Receive")],
            "column": 10
        },
        "PrEditor_Receive_TotalCases": {
            "conditions": [(15, "Total"), (14, "Case"), (1, "PrEditor Receive")],
            "column": 16
        },
        "SmallsTotal": {
            "conditions": [(15, "Small")],
            "column": 16
        },
        "Total": {
            "conditions": [(15, "Total")],
            "column": 16
        },
        "PID CASES": {
            "conditions": [(1, "PID Receive"), (14, "Case"), (15, "Total")],
            "column": 16
        }
    }
}

def process_PPR_LP_Receive(df: DataFrame,
                           generic_process,
                           PPR_JSON: Dict[str, Any],
                           config: Dict[str, Any]) -> None:
    logging.info("Processing PPR_LP_Receive...")
    if "PPR_LP_Receive" not in PPR_JSON:
        PPR_JSON["PPR_LP_Receive"] = {}

    generic_process(df, "PPR_LP_Receive", PPR_JSON, config)
    logging.info("Finished PPR_LP_Receive.")
