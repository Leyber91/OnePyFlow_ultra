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
        "Each_Receive_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "Each Receive")],
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

def process_PPR_Each_Receive(df: DataFrame,
                             generic_process,
                             PPR_JSON: Dict[str, Any],
                             config: Dict[str, Any]) -> None:
    logging.info("Processing PPR_Each_Receive...")
    if "PPR_Each_Receive" not in PPR_JSON:
        PPR_JSON["PPR_Each_Receive"] = {}

    generic_process(df, "PPR_Each_Receive", PPR_JSON, config)
    logging.info("Finished PPR_Each_Receive.")
