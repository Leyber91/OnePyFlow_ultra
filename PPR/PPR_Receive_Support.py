# PPR_Receive_Support.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "Receive_Support_function_name": 1,
        "Receive_Support_paid_hours": 10,
        "Receive_Support_unit_type": 14,
        "Receive_Support_size": 15,
        "Receive_Support_units": 16
    },
    "sums": {
        "Decant_NonTI_Units": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "Decant Non-TI")],
            "column": 16
        },
        "Decant_NonTI_Hours": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "Decant Non-TI")],
            "column": 10
        },
        "Cases_Decanat": {
            "conditions": [(15, "Total"), (14, "Case"), (1, "Decant Non-TI")],
            "column": 16
        },
        "SmallsTotal": {
            "conditions": [(15, "Small")],
            "column": 16
        },
        "Total": {
            "conditions": [(15, "Total")],
            "column": 16
        }
    }
}

def process_PPR_Receive_Support(df: DataFrame,
                                generic_process,
                                PPR_JSON: Dict[str, Any],
                                config: Dict[str, Any]) -> None:
    logging.info("Processing PPR_Receive_Support...")
    if "PPR_Receive_Support" not in PPR_JSON:
        PPR_JSON["PPR_Receive_Support"] = {}

    generic_process(df, "PPR_Receive_Support", PPR_JSON, config)
    logging.info("Finished PPR_Receive_Support.")
